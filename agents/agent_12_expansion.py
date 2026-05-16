"""
Agent 12: Subscription Expansion Agent
Manages transition from pilot to subscription, and identifies expansion opportunities.
"""
from typing import Dict
from agents.base import BaseAgent
from config import MODEL_COMPLEX, EXPANSION_ARR_THRESHOLD


class SubscriptionExpansionAgent(BaseAgent):
    name = "Agent 12 - Subscription Expansion"
    model = MODEL_COMPLEX
    system_prompt = """You are the Subscription Expansion Agent for Inshira Technologies.

Your role:
- Manage the transition from pilot to annual subscription
- Identify expansion opportunities within existing accounts
- Monitor renewal risk and flag it early
- Track value delivered against what was promised in the proposal

Account health scoring (0-100):
- Engagement quality (40 pts): frequency and quality of interactions
- Value delivery (30 pts): measurable outcomes vs promised ROI
- Champion stability (15 pts): primary contact still in role and engaged
- Breadth of relationship (15 pts): multiple stakeholders engaged

Renewal risk levels:
- Low (80-100): on track, proactive value delivery
- Medium (60-79): some engagement decline or delivery gap
- High (40-59): significant risk, escalate to founder
- Critical (<40): immediate founder intervention required

Expansion triggers:
- New production line or process identified
- New site or facility
- New pain category discovered post-subscription
- Annual review surfacing unresolved operational losses

Flag expansion opportunities >£25k additional ARR for Checkpoint 8."""

    def run(self, context: Dict) -> Dict:
        """
        context keys:
          - company: company record
          - subscription: subscription record
          - relationship_data: from Agent 06
          - roi_delivered: actual vs promised ROI data
          - recent_interactions: list of recent touchpoints
        """
        company = context.get("company", {})
        subscription = context.get("subscription", {})
        prompt = f"""
Analyse this active subscription account and produce an expansion and health report.

Company: {company}

Subscription details:
{subscription}

Relationship data:
{context.get('relationship_data', {{}})}

ROI delivered vs promised:
{context.get('roi_delivered', 'Not yet measured.')}

Recent interactions:
{context.get('recent_interactions', [])}

Produce:
{{
  "company_id": "{company.get('company_id', '')}",
  "subscription_id": "{subscription.get('subscription_id', '')}",
  "account_health_score": 0,
  "health_breakdown": {{
    "engagement_quality": 0,
    "value_delivery": 0,
    "champion_stability": 0,
    "relationship_breadth": 0
  }},
  "renewal_risk": "Low|Medium|High|Critical",
  "renewal_risk_factors": ["..."],
  "champion_stability": "Stable|At Risk|Changed",
  "expansion_opportunities": [
    {{
      "description": "...",
      "expansion_arr_estimate": 0,
      "pilot_angle": "...",
      "readiness": "Now|3 Months|6 Months",
      "checkpoint_8_required": true/false
    }}
  ],
  "recommended_actions": ["..."],
  "next_review_date": "...",
  "escalate_to_founder": true/false,
  "escalation_reason": "..."
}}
"""
        result = self._call_json(prompt, max_tokens=4096)

        # Update subscription health score
        if result.get("account_health_score") is not None:
            self.crm.upsert_subscription({
                "subscription_id": subscription.get("subscription_id"),
                "company_id": company.get("company_id"),
                "account_health_score": result["account_health_score"],
                "renewal_risk": result.get("renewal_risk"),
            })

        self.crm.log("agent_12_run", {
            "company_id": company.get("company_id"),
            "health_score": result.get("account_health_score"),
            "renewal_risk": result.get("renewal_risk"),
            "escalate": result.get("escalate_to_founder", False),
        })
        return result
