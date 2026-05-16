"""
Agent 09: Discovery Preparation Agent
Prepares the founder for every discovery conversation.
"""
from typing import Dict
from agents.base import BaseAgent
from config import MODEL_COMPLEX


class DiscoveryPreparationAgent(BaseAgent):
    name = "Agent 09 - Discovery Preparation"
    model = MODEL_COMPLEX
    system_prompt = """You are the Discovery Preparation Agent for Inshira Technologies.

Your role:
- Prepare the founder or sales lead for every discovery conversation
- Produce a complete meeting intelligence pack: company brief, questions, stakeholder map
- Questions must be structured for manufacturing context — not generic sales discovery

Discovery preparation principles:
- Questions should validate or refute specific pain hypotheses — not fish generically
- Questions should show operational credibility (you understand manufacturing)
- Maximum 7 questions; each must be open-ended and non-threatening
- Stakeholder map must identify who attends, their likely concerns, and decision-making role
- Always include suggested pilot angles based on hypotheses
- Flag any relationship sensitivities before the call

Good discovery questions for manufacturers:
- 'Where do you currently have visibility on [specific process]?'
- 'When a job overruns its budget, what's the first signal you get?'
- 'How do you currently track [OEE/energy/scrap] at the job level?'
- 'What does a bad week look like operationally for your team?'
- 'If you could fix one thing about [process], what would it be?'

Post-call output: note template for updating CRM and hypothesis accuracy log."""

    def run(self, context: Dict) -> Dict:
        """
        context keys:
          - company: enriched company record
          - operational_brief: from Agent 04
          - hypotheses: from Agent 05
          - contacts: list of contacts attending meeting
          - relationship_data: from Agent 06
          - meeting_date: when the call is scheduled
        """
        company = context.get("company", {})
        hypotheses = context.get("hypotheses", [])
        contacts = context.get("contacts", [])

        prompt = f"""
Prepare a complete discovery call intelligence pack for this manufacturing prospect.

Company: {company.get('company_name', 'Unknown')}
Sector: {company.get('sector', '')}
Manufacturing type: {company.get('manufacturing_type', '')}
Pipeline stage: {company.get('pipeline_stage', '')}
Meeting date: {context.get('meeting_date', 'TBD')}

Operational intelligence brief:
{context.get('operational_brief', 'See company profile above.')}

Pain hypotheses:
{hypotheses}

Contacts attending:
{contacts}

Relationship context:
{context.get('relationship_data', {{}})}

Produce a complete discovery prep pack:
{{
  "company_id": "{company.get('company_id', '')}",
  "company_brief": "...",
  "meeting_objectives": ["..."],
  "discovery_questions": [
    {{
      "question": "...",
      "hypothesis_it_tests": "...",
      "expected_signal_if_pain_exists": "...",
      "follow_up_if_yes": "..."
    }}
  ],
  "stakeholder_map": [
    {{
      "contact_id": "...",
      "name": "...",
      "role": "...",
      "likely_concerns": ["..."],
      "influence": "Low|Medium|High",
      "suggested_approach": "..."
    }}
  ],
  "competitor_context": "...",
  "suggested_pilot_angles": ["..."],
  "relationship_sensitivities": ["..."],
  "next_step_framework": {{
    "ideal_outcome": "...",
    "pilot_offer_logic": "...",
    "fallback_if_not_ready": "..."
  }},
  "pre_call_checklist": ["..."],
  "post_call_note_template": "..."
}}
"""
        result = self._call_json(prompt, max_tokens=6000)
        self.crm.log("agent_09_run", {
            "company_id": company.get("company_id"),
            "questions_generated": len(result.get("discovery_questions", [])),
        })
        return result
