"""
Inshira Growth OS - CRM & Memory Layer
Five entity types stored as JSON files in data/.
Agent 13 is the custodian; all agents read/write via this class.
"""
import json
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from config import DATA_DIR


def _now() -> str:
    return datetime.utcnow().isoformat()


def _load(path: str) -> List[Dict]:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def _save(path: str, data: List[Dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class CRM:
    """Single source of truth for all swarm operations."""

    ENTITIES = ["companies", "contacts", "outreach", "pilots", "subscriptions", "logs"]

    def __init__(self):
        self.paths = {e: os.path.join(DATA_DIR, f"{e}.json") for e in self.ENTITIES}

    # ------------------------------------------------------------------ #
    # Generic helpers
    # ------------------------------------------------------------------ #

    def _all(self, entity: str) -> List[Dict]:
        return _load(self.paths[entity])

    def _write(self, entity: str, records: List[Dict]) -> None:
        _save(self.paths[entity], records)

    def _upsert(self, entity: str, id_field: str, record: Dict) -> Dict:
        records = self._all(entity)
        for i, r in enumerate(records):
            if r.get(id_field) == record.get(id_field):
                records[i] = {**r, **record, "last_updated": _now()}
                _save(self.paths[entity], records)
                return records[i]
        record[id_field] = record.get(id_field) or str(uuid.uuid4())
        record["created_at"] = _now()
        record["last_updated"] = _now()
        records.append(record)
        _save(self.paths[entity], records)
        return record

    def _find(self, entity: str, id_field: str, value: str) -> Optional[Dict]:
        for r in self._all(entity):
            if r.get(id_field) == value:
                return r
        return None

    def _filter(self, entity: str, **kwargs) -> List[Dict]:
        results = self._all(entity)
        for key, val in kwargs.items():
            results = [r for r in results if r.get(key) == val]
        return results

    # ------------------------------------------------------------------ #
    # Company Memory (Layer 1)
    # ------------------------------------------------------------------ #

    def upsert_company(self, record: Dict) -> Dict:
        return self._upsert("companies", "company_id", record)

    def get_company(self, company_id: str) -> Optional[Dict]:
        return self._find("companies", "company_id", company_id)

    def all_companies(self) -> List[Dict]:
        return self._all("companies")

    def companies_by_stage(self, stage: str) -> List[Dict]:
        return self._filter("companies", pipeline_stage=stage)

    def companies_above_score(self, min_score: int) -> List[Dict]:
        return [c for c in self._all("companies") if (c.get("icp_fit_score") or 0) >= min_score]

    def update_company_stage(self, company_id: str, stage: str) -> None:
        company = self.get_company(company_id)
        if company:
            company["pipeline_stage"] = stage
            self.upsert_company(company)

    # ------------------------------------------------------------------ #
    # Relationship Memory (Layer 2)
    # ------------------------------------------------------------------ #

    def upsert_contact(self, record: Dict) -> Dict:
        return self._upsert("contacts", "contact_id", record)

    def get_contact(self, contact_id: str) -> Optional[Dict]:
        return self._find("contacts", "contact_id", contact_id)

    def contacts_for_company(self, company_id: str) -> List[Dict]:
        return self._filter("contacts", company_id=company_id)

    def update_trust_score(self, contact_id: str, delta: int, reason: str) -> int:
        contact = self.get_contact(contact_id)
        if not contact:
            return 0
        current = contact.get("trust_score", 0)
        new_score = max(0, min(100, current + delta))
        contact["trust_score"] = new_score
        # Update maturity stage
        from config import TRUST_SCORE_STAGES
        for stage, (lo, hi) in TRUST_SCORE_STAGES.items():
            if lo <= new_score <= hi:
                contact["relationship_maturity"] = stage
                break
        self.upsert_contact(contact)
        self.log("trust_update", {"contact_id": contact_id, "delta": delta,
                                   "new_score": new_score, "reason": reason})
        return new_score

    # ------------------------------------------------------------------ #
    # Campaign Memory (Layer 3)
    # ------------------------------------------------------------------ #

    def upsert_outreach(self, record: Dict) -> Dict:
        return self._upsert("outreach", "outreach_id", record)

    def outreach_for_company(self, company_id: str) -> List[Dict]:
        return self._filter("outreach", company_id=company_id)

    def outreach_pending_approval(self) -> List[Dict]:
        return self._filter("outreach", approval_status="Pending")

    def approve_outreach(self, outreach_id: str, approver: str) -> None:
        rec = self._find("outreach", "outreach_id", outreach_id)
        if rec:
            rec["approval_status"] = "Approved"
            rec["approved_by"] = approver
            self.upsert_outreach(rec)

    def reject_outreach(self, outreach_id: str, reason: str = "") -> None:
        rec = self._find("outreach", "outreach_id", outreach_id)
        if rec:
            rec["approval_status"] = "Rejected"
            rec["rejection_reason"] = reason
            self.upsert_outreach(rec)

    # ------------------------------------------------------------------ #
    # Pilot Memory (Layer 4)
    # ------------------------------------------------------------------ #

    def upsert_pilot(self, record: Dict) -> Dict:
        return self._upsert("pilots", "pilot_id", record)

    def get_pilot(self, pilot_id: str) -> Optional[Dict]:
        return self._find("pilots", "pilot_id", pilot_id)

    def pilots_for_company(self, company_id: str) -> List[Dict]:
        return self._filter("pilots", company_id=company_id)

    def active_pilots(self) -> List[Dict]:
        return self._filter("pilots", status="Active")

    # ------------------------------------------------------------------ #
    # Subscription Memory (Layer 5)
    # ------------------------------------------------------------------ #

    def upsert_subscription(self, record: Dict) -> Dict:
        return self._upsert("subscriptions", "subscription_id", record)

    def get_subscription(self, subscription_id: str) -> Optional[Dict]:
        return self._find("subscriptions", "subscription_id", subscription_id)

    def subscriptions_for_company(self, company_id: str) -> List[Dict]:
        return self._filter("subscriptions", company_id=company_id)

    def at_risk_subscriptions(self) -> List[Dict]:
        return [s for s in self._all("subscriptions")
                if (s.get("account_health_score") or 100) < 60]

    # ------------------------------------------------------------------ #
    # Audit Log
    # ------------------------------------------------------------------ #

    def log(self, event_type: str, payload: Dict) -> None:
        logs = _load(self.paths["logs"])
        logs.append({
            "log_id": str(uuid.uuid4()),
            "timestamp": _now(),
            "event_type": event_type,
            "payload": payload,
        })
        _save(self.paths["logs"], logs)

    def recent_logs(self, n: int = 50) -> List[Dict]:
        return self._all("logs")[-n:]

    # ------------------------------------------------------------------ #
    # Pipeline summary
    # ------------------------------------------------------------------ #

    def pipeline_summary(self) -> Dict[str, int]:
        stages = {}
        for c in self._all("companies"):
            s = c.get("pipeline_stage", "Unknown")
            stages[s] = stages.get(s, 0) + 1
        return stages
