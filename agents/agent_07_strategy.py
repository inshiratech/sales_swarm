"""
Agent 07: Outreach Strategy Agent
Designs sequencing, channel selection, timing, and angle for every outreach campaign.
"""
from typing import Dict
from agents.base import BaseAgent
from config import MODEL_COMPLEX, MAX_TOUCHES_PER_SEQUENCE, TOUCH_1_DAY, TOUCH_2_DAY, TOUCH_3_DAY


class OutreachStrategyAgent(BaseAgent):
    name = "Agent 07 - Outreach Strategy"
    model = MODEL_COMPLEX
    system_prompt = """You are the Outreach Strategy Agent for Inshira Technologies.

Your role:
- Design multi-touch outreach sequences for each lead
- Select the right channel, timing, and angle for every touchpoint
- Never design aggressive or spammy sequences
- Flag strategic accounts for founder-led outreach

Sequence rules:
- Maximum 3 touches per initial sequence
- Touch 1: Day 0 — Email, primary pain hypothesis
- Touch 2: Day 8 (if no reply) — Email or LinkedIn, secondary hypothesis
- Touch 3: Day 18 (if no reply) — Email, value-add sector insight
- After 3 non-responses: move to nurture pool, set trigger event for re-engagement
- NO bump emails ("just circling back"). If 3 touches fail, change the angle — never chase.

Channel selection:
- Email: primary channel for initial outreach
- LinkedIn: warm-up before email, or as Touch 2 alternative
- Phone: only when contact has engaged (Aware stage minimum)
- Event/referral: when sector event or warm intro is identified

Founder-led mode: strategic accounts (Priority A, score 85+) always go to Checkpoint 3
with mandatory founder review. Standard accounts: commercial lead can approve."""

    def run(self, context: Dict) -> Dict:
        """
        context keys:
          - company: enriched company record
          - hypotheses: from Agent 05
          - relationship_data: from Agent 06
          - campaign_performance: from Agent 14
          - priority_band: A/B/C/D
        """
        company = context.get("company", {})
        hypotheses = context.get("hypotheses", [])
        primary_h = hypotheses[0] if hypotheses else {}

        prompt = f"""
Design a complete outreach sequence for this manufacturing prospect.

Company:
{company}

Pain hypotheses (ranked):
{hypotheses}

Relationship data:
{context.get('relationship_data', {{'relationship_maturity': 'Cold', 'trust_score': 0}})}

Priority band: {context.get('priority_band', 'B')}

Campaign performance data (what angles/channels are working):
{context.get('campaign_performance', 'No performance data yet — use best judgement.')}

Design the outreach sequence:
{{
  "company_id": "{company.get('company_id', '')}",
  "sequence_name": "...",
  "founder_led": true/false,
  "priority_band": "A|B|C|D",
  "touches": [
    {{
      "touch_number": 1,
      "send_day": {TOUCH_1_DAY},
      "channel": "Email|LinkedIn|Phone",
      "pain_hypothesis_index": 0,
      "outreach_angle": "...",
      "message_variant": "A",
      "goal": "...",
      "follow_up_logic": "..."
    }},
    {{
      "touch_number": 2,
      "send_day": {TOUCH_2_DAY},
      "channel": "Email|LinkedIn",
      "pain_hypothesis_index": 1,
      "outreach_angle": "...",
      "message_variant": "A",
      "goal": "...",
      "follow_up_logic": "..."
    }},
    {{
      "touch_number": 3,
      "send_day": {TOUCH_3_DAY},
      "channel": "Email",
      "pain_hypothesis_index": 0,
      "outreach_angle": "value_add_insight",
      "message_variant": "A",
      "goal": "...",
      "follow_up_logic": "Move to nurture after this touch if no reply"
    }}
  ],
  "nurture_trigger": "...",
  "checkpoint_3_required": true,
  "sequence_notes": "..."
}}
"""
        result = self._call_json(prompt)
        self.crm.log("agent_07_run", {
            "company_id": company.get("company_id"),
            "sequence_name": result.get("sequence_name"),
            "founder_led": result.get("founder_led", False),
        })
        return result
