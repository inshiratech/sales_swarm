"""
Agent 06: Relationship Intelligence Agent
Maintains the full relationship map for every prospect and customer.
"""
from typing import Dict
from agents.base import BaseAgent
from config import MODEL_COMPLEX


class RelationshipIntelligenceAgent(BaseAgent):
    name = "Agent 06 - Relationship Intelligence"
    model = MODEL_COMPLEX
    system_prompt = """You are the Relationship Intelligence Agent for Inshira Technologies.

Your role:
- Maintain the full relationship map for every prospect and customer
- Track trust, engagement, and relationship maturity over time
- Identify positive reply signals that require immediate founder escalation
- Flag relationship decay and recommend re-engagement actions

Trust score events:
- Positive first reply: +15
- Discovery call completed: +20
- Pilot agreed and started: +15
- Pilot delivered on time: +10
- ROI validated: +10
- Subscription signed: +5
- Silent 30 days: -5
- Silent 60 days: -10
- Negative/annoyed reply: -20
- Champion departs: -15
- Inshira misses a commitment: -25

Relationship maturity stages:
- Cold (0-20): first-touch, manufacturing-grounded outreach
- Aware (21-40): second touch, different angle
- Engaged (41-60): conversation mode, discovery call
- Trusting (61-80): pilot/proposal stage
- Partner (81-100): paying customer, expansion focus

CRITICAL: Trust drops >15 points must be flagged for immediate human review.
Positive replies from any account must escalate to founder WITHIN 1 HOUR."""

    def run(self, context: Dict) -> Dict:
        """
        context keys:
          - company_id: company to assess
          - event_type: trust event that occurred (optional)
          - event_details: details of the event (optional)
          - contacts: list of contacts for this company
          - recent_outreach: recent outreach records
        """
        company_id = context.get("company_id", "")
        contacts = context.get("contacts", self.crm.contacts_for_company(company_id))
        outreach = context.get("recent_outreach", self.crm.outreach_for_company(company_id))

        prompt = f"""
Analyse the relationship status for company {company_id} and produce a relationship brief.

Contacts:
{contacts}

Recent outreach activity:
{outreach[-10:] if outreach else 'No outreach yet.'}

Event that occurred (if any):
Type: {context.get('event_type', 'None')}
Details: {context.get('event_details', 'N/A')}

Produce:
{{
  "company_id": "{company_id}",
  "relationship_brief": {{
    "primary_contact": "...",
    "trust_score": 0,
    "relationship_maturity": "Cold|Aware|Engaged|Trusting|Partner",
    "days_since_last_contact": 0,
    "decay_flag": true/false,
    "decay_severity": "None|Warning|Flag|Critical"
  }},
  "trust_score_updates": [
    {{
      "contact_id": "...",
      "delta": 0,
      "reason": "...",
      "new_score": 0
    }}
  ],
  "stakeholder_map": [
    {{
      "contact_id": "...",
      "role": "...",
      "influence": "Low|Medium|High",
      "decision_maker": true/false,
      "relationship_health": "..."
    }}
  ],
  "recommended_next_action": "...",
  "escalate_to_founder": true/false,
  "escalation_reason": "...",
  "escalation_urgency": "Immediate|Same Day|48 Hours|None",
  "positive_reply_detected": true/false,
  "objections_raised": ["..."]
}}
"""
        result = self._call_json(prompt, max_tokens=4096)

        # Apply trust score updates
        for update in result.get("trust_score_updates", []):
            if update.get("contact_id") and update.get("delta"):
                self.crm.update_trust_score(
                    update["contact_id"],
                    update["delta"],
                    update.get("reason", ""),
                )

        self.crm.log("agent_06_run", {
            "company_id": company_id,
            "escalate": result.get("escalate_to_founder", False),
            "positive_reply": result.get("positive_reply_detected", False),
        })
        return result
