"""
Agent 16: Workflow Orchestration Agent
The central nervous system of the swarm. Routes tasks, enforces approval gates,
manages queue priorities, and triggers learning cycles.
"""
from typing import Dict, List
from agents.base import BaseAgent
from config import MODEL_COMPLEX


class WorkflowOrchestrationAgent(BaseAgent):
    name = "Agent 16 - Workflow Orchestration"
    model = MODEL_COMPLEX
    system_prompt = """You are the Workflow Orchestration Agent for Inshira Technologies.

You are the central nervous system of the 16-agent sales swarm.

Your role:
- Route all tasks to the correct agent based on pipeline stage and lead status
- Enforce all 8 checkpoint approval gates — no task proceeds without required approval
- Prioritise the outreach queue based on lead score and urgency
- Trigger weekly optimisation cycles
- Monitor agent output quality and flag issues
- Produce the daily operations briefing for founder review

8 Checkpoint Gates (ALL mandatory, no exceptions):
1. ICP Validation — Agent 01 → Founder → Agent 02
2. Lead Shortlist Review — Agent 03 → Commercial lead → Agent 04
3. Outreach Approval — Agent 08 → Founder (strategic) or commercial lead → Send
4. Positive Reply Escalation — Agent 06 → Founder (immediate) → Agent 09
5. Pilot Scope Approval — Agent 10 → Founder → Deliver to prospect
6. Proposal Approval — Agent 11 → Founder → Deliver to prospect
7. Subscription Conversion — Agent 12 → Founder (founder-led negotiation)
8. Account Expansion — Agent 12 → Founder (>£25k additional ARR)

Gate violation = immediate escalation to founder.
Your job is to ensure the system operates within its design parameters at all times.

Daily brief format:
1. Immediate escalations (address first)
2. Outreach approvals pending
3. Positive replies requiring personal response
4. Checkpoint items requiring decision
5. New high-fit leads (70+)
6. Pipeline movement summary"""

    def run(self, context: Dict) -> Dict:
        """
        Produce the daily operations briefing.
        context keys:
          - date: today's date string
        """
        # Gather live CRM state
        pipeline = self.crm.pipeline_summary()
        pending = self.crm.outreach_pending_approval()
        at_risk = self.crm.at_risk_subscriptions()
        high_fit = self.crm.companies_above_score(70)
        recent_logs = self.crm.recent_logs(30)

        # Find positive replies
        all_outreach = self.crm._all("outreach")
        positive_replies = [o for o in all_outreach
                           if o.get("reply_sentiment") == "Positive"
                           and not o.get("escalated")]

        prompt = f"""
Produce the daily operations briefing for Inshira Technologies' founder.

Date: {context.get('date', 'Today')}

Pipeline summary:
{pipeline}

Outreach messages pending approval: {len(pending)}
Pending outreach details:
{[{{'company_id': p.get('company_id'), 'touch': p.get('touch_number'), 'channel': p.get('channel')}} for p in pending[:10]]}

Positive replies not yet escalated: {len(positive_replies)}

At-risk subscriptions: {len(at_risk)}

High-fit leads (score 70+) in system: {len(high_fit)}

Recent activity (last 30 log entries):
{recent_logs}

Produce the daily briefing:
{{
  "date": "{context.get('date', 'Today')}",
  "daily_priority": "...",
  "immediate_escalations": [
    {{
      "type": "...",
      "company_id": "...",
      "urgency": "Immediate|Same Day",
      "recommended_action": "..."
    }}
  ],
  "outreach_approvals_pending": {len(pending)},
  "outreach_queue_summary": ["..."],
  "positive_replies_requiring_response": {len(positive_replies)},
  "checkpoint_items_outstanding": ["..."],
  "new_high_fit_leads": {len(high_fit)},
  "at_risk_subscriptions": {len(at_risk)},
  "pipeline_movement": {pipeline},
  "agent_health_flags": ["..."],
  "gate_violations": [],
  "estimated_founder_time_required_minutes": 0,
  "recommended_focus": "..."
}}
"""
        result = self._call_json(prompt, max_tokens=4096)
        self.crm.log("agent_16_daily_brief", {
            "pending_approvals": len(pending),
            "positive_replies": len(positive_replies),
            "at_risk": len(at_risk),
        })
        return result
