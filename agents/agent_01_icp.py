"""
Agent 01: ICP Intelligence Agent
Maintains, refines, and validates Inshira's Ideal Customer Profile.
"""
from typing import Dict
from agents.base import BaseAgent
from config import MODEL_COMPLEX


class ICPIntelligenceAgent(BaseAgent):
    name = "Agent 01 - ICP Intelligence"
    model = MODEL_COMPLEX
    system_prompt = """You are the ICP Intelligence Agent for Inshira Technologies, a B2B SaaS company
that helps UK SME manufacturers find and fix operational losses.

Your role:
- Maintain, refine, and validate the Ideal Customer Profile (ICP)
- Translate market intelligence into actionable targeting criteria
- Prevent effort being wasted on low-fit leads
- Analyse incoming lead and conversion data to update ICP scoring weights

ICP Definition (current baseline):
- Geography: UK-based manufacturers
- Headcount: 20-500 employees
- Sectors: Precision Engineering, Metal Fabrication, Plastics/Composites, Food & Beverage,
  Packaging, Aerospace Components, Automotive Components, Electronics Assembly
- Manufacturing type: Bespoke, High-Mix, Volume, Process, Assembly
- Data maturity: Basic Digital to ERP (manual-only companies are low priority)
- Energy/operational complexity: Medium-High preferred
- Decision-maker: MD, Operations Director, Factory Manager

Your outputs must include:
- Updated ICP criteria with scoring weights
- Sector priority rankings (1=highest)
- Persona targeting guidelines
- Whether a material ICP change requires founder approval (Checkpoint 1)

You are a rigorous analyst. Never recommend chasing leads that don't fit the ICP just to fill a pipeline."""

    def run(self, context: Dict) -> Dict:
        """
        context keys:
          - conversion_data: list of recent won/lost deals
          - sector_intelligence: briefing from Agent 15
          - pilot_outcomes: list of pilot results
          - current_icp: existing ICP definition dict
        """
        prompt = f"""
Analyse the following data and produce an updated ICP validation report.

Current ICP definition:
{context.get('current_icp', 'Not yet defined — produce initial ICP.')}

Recent conversion data (won/lost deals):
{context.get('conversion_data', 'No conversion data yet.')}

Sector intelligence from Agent 15:
{context.get('sector_intelligence', 'No sector intelligence yet.')}

Pilot outcomes:
{context.get('pilot_outcomes', 'No pilot outcomes yet.')}

Produce a JSON object with:
{{
  "icp_summary": "...",
  "sector_priorities": [{{"sector": "...", "priority_rank": 1, "rationale": "..."}}],
  "scoring_weights": {{
    "icp_fit": 15,
    "operational_pain_likelihood": 20,
    "data_maturity": 10,
    "pilot_suitability": 15,
    "subscription_potential": 10,
    "urgency": 10,
    "ability_to_pay": 10,
    "relationship_warmth": 5,
    "decision_maker_access": 5
  }},
  "persona_guidelines": ["..."],
  "material_change_detected": true/false,
  "checkpoint_1_required": true/false,
  "change_rationale": "...",
  "recommendations": ["..."]
}}
"""
        result = self._call_json(prompt)
        self.crm.log("agent_01_run", {"output_keys": list(result.keys())})
        return result
