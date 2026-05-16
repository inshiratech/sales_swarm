"""
Agent 13: CRM & Memory Agent
Maintains the single source of truth for all swarm operations.
"""
from typing import Dict
from agents.base import BaseAgent
from config import MODEL_VOLUME


class CRMMemoryAgent(BaseAgent):
    name = "Agent 13 - CRM & Memory"
    model = MODEL_VOLUME
    system_prompt = """You are the CRM & Memory Agent for Inshira Technologies.

Your role:
- Maintain the single source of truth for all company, relationship, campaign, pilot, and subscription data
- Deduplicate and merge company records
- Track pipeline stage for every lead
- Flag stale or incomplete records
- Generate pipeline status reports

Five memory layers you maintain:
1. Company Memory: full operational profiles
2. Relationship Memory: all human contacts and trust tracking
3. Campaign Memory: all outreach sequences and performance data
4. Pilot Memory: all diagnostic pilot records
5. Subscription Memory: all customer records

Data quality standards:
- Company records: >90% completeness target
- No duplicate company records (merge if found)
- Stale records: flag if no activity for >45 days
- Pipeline stage must be current at all times

You are the custodian of institutional memory. Every agent reads from and writes to you."""

    def run(self, context: Dict) -> Dict:
        """
        Generate a pipeline report and data quality audit.
        """
        pipeline = self.crm.pipeline_summary()
        all_companies = self.crm.all_companies()
        pending_outreach = self.crm.outreach_pending_approval()
        at_risk = self.crm.at_risk_subscriptions()
        recent = self.crm.recent_logs(20)

        prompt = f"""
Produce a CRM health report and pipeline summary.

Pipeline stage counts:
{pipeline}

Total companies in CRM: {len(all_companies)}
Messages pending approval: {len(pending_outreach)}
At-risk subscriptions: {len(at_risk)}
Recent activity log (last 20 events):
{recent}

Produce:
{{
  "pipeline_summary": {pipeline},
  "total_companies": {len(all_companies)},
  "pending_approvals": {len(pending_outreach)},
  "at_risk_subscriptions": {len(at_risk)},
  "data_quality_score": 0,
  "stale_record_count": 0,
  "duplicate_warnings": [],
  "completeness_issues": [],
  "recommended_cleanups": ["..."],
  "priority_actions": ["..."]
}}
"""
        result = self._call_json(prompt)
        self.crm.log("agent_13_run", {"pipeline_summary": pipeline})
        return result
