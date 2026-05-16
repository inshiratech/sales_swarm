"""
Agent 14: Learning & Optimisation Agent
Analyses all system performance data to continuously improve the swarm.
"""
from typing import Dict, List
from agents.base import BaseAgent
from config import MODEL_COMPLEX


class LearningOptimisationAgent(BaseAgent):
    name = "Agent 14 - Learning & Optimisation"
    model = MODEL_COMPLEX
    system_prompt = """You are the Learning & Optimisation Agent for Inshira Technologies.

Your role:
- Analyse all system performance data to continuously improve the swarm
- Produce weekly optimisation reports with actionable recommendations
- Identify top-performing message variants, outreach angles, and sectors
- Update sector pain pattern library based on validated discoveries

Four learning loops you manage:
1. Messaging Performance (weekly): reply rates by variant, angle, channel
2. Hypothesis Validation (after each discovery call): which hypotheses are accurate
3. Sector Engagement Analysis (monthly): which sectors respond best
4. Pilot & ROI Intelligence (after each pilot): did our ROI estimates match reality?

KPI thresholds to flag:
- Reply rate <5% over 4 weeks: systemic failure, escalate to founder
- Hypothesis accuracy <40%: retire and replace hypotheses
- Sector engagement <3% reply rate over 8 weeks: ICP review needed
- ROI estimate variance >50%: update modelling methodology

Weekly report must include: specific recommendations, not vague observations.
Every recommendation must name the agent it goes to and what to change."""

    def run(self, context: Dict) -> Dict:
        """
        context keys:
          - outreach_records: all outreach from last 7 days
          - discovery_call_notes: post-call notes with hypothesis validation
          - pilot_outcomes: completed pilot data
          - period: 'weekly' or 'monthly'
        """
        outreach = context.get("outreach_records",
                               self.crm._all("outreach"))
        period = context.get("period", "weekly")

        # Calculate basic performance metrics
        total_sent = [o for o in outreach if o.get("sent_date")]
        replied = [o for o in total_sent if o.get("reply_received")]
        positive = [o for o in replied if o.get("reply_sentiment") == "Positive"]

        reply_rate = (len(replied) / len(total_sent) * 100) if total_sent else 0
        positive_rate = (len(positive) / len(total_sent) * 100) if total_sent else 0

        prompt = f"""
Produce a {period} learning and optimisation report for the Inshira Growth OS swarm.

Outreach performance:
- Total messages sent: {len(total_sent)}
- Replies received: {len(replied)} ({reply_rate:.1f}% reply rate)
- Positive replies: {len(positive)} ({positive_rate:.1f}% positive rate)

Discovery call notes (hypothesis validation):
{context.get('discovery_call_notes', 'No discovery call data yet.')}

Pilot outcomes:
{context.get('pilot_outcomes', 'No pilot outcomes yet.')}

Sector engagement data:
{context.get('sector_data', 'Not enough data yet.')}

Produce a structured optimisation report:
{{
  "period": "{period}",
  "overall_health": "Healthy|Warning|Critical",
  "pipeline_velocity": {{
    "leads_moved_this_week": 0,
    "bottleneck_stage": "...",
    "bottleneck_reason": "..."
  }},
  "outreach_performance": {{
    "reply_rate_pct": {reply_rate:.1f},
    "positive_reply_rate_pct": {positive_rate:.1f},
    "best_performing_angle": "...",
    "worst_performing_angle": "...",
    "best_channel": "...",
    "systemic_failure_flag": {str(reply_rate < 5 and len(total_sent) > 20).lower()}
  }},
  "hypothesis_accuracy": {{
    "validated_this_period": 0,
    "refuted_this_period": 0,
    "accuracy_rate_pct": 0,
    "hypotheses_to_retire": ["..."],
    "new_patterns_identified": ["..."]
  }},
  "sector_heatmap": [
    {{
      "sector": "...",
      "reply_rate_pct": 0,
      "status": "Hot|Warm|Cold|Inactive"
    }}
  ],
  "objection_register": [
    {{
      "objection": "...",
      "frequency": 0,
      "suggested_counter": "..."
    }}
  ],
  "recommendations": [
    {{
      "agent": "Agent 01|05|07|08",
      "action": "...",
      "rationale": "...",
      "priority": "High|Medium|Low"
    }}
  ],
  "alerts": ["..."],
  "next_week_priorities": ["..."]
}}
"""
        result = self._call_json(prompt, max_tokens=6000)
        self.crm.log("agent_14_run", {
            "period": period,
            "reply_rate": reply_rate,
            "systemic_failure": result.get("outreach_performance", {}).get("systemic_failure_flag", False),
        })
        return result
