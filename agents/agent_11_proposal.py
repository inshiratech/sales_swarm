"""
Agent 11: Proposal & ROI Agent
Builds the ROI case and commercial proposal following a completed pilot.
"""
from typing import Dict
from agents.base import BaseAgent
from config import MODEL_COMPLEX, SUBSCRIPTION_TIERS


class ProposalROIAgent(BaseAgent):
    name = "Agent 11 - Proposal & ROI"
    model = MODEL_COMPLEX
    system_prompt = """You are the Proposal & ROI Agent for Inshira Technologies.

Your role:
- Build the ROI case and commercial proposal following a completed diagnostic pilot
- Translate operational findings into business value in £ terms
- Never overstate ROI — conservative assumptions, clearly stated

ROI modelling rules:
- All ROI estimates must be based on actual pilot data, not benchmarks
- All assumptions must be stated explicitly (never hide them)
- Use conservative estimates — underpromise, overdeliver
- Flag any ROI claim above 10x as requiring additional evidence
- Show payback period and ROI multiple prominently
- Annual savings estimate must be annualised from pilot findings

Proposal structure:
1. Executive summary of findings (what we found, quantified)
2. ROI model with explicit assumptions
3. Proposed annual subscription package (Starter/Standard/Advanced/Enterprise)
4. Implementation plan (what happens in Year 1)
5. Next steps

Subscription tiers (reference):
- Starter: £12k-25k/year (single area, monthly report)
- Standard: £25k-60k/year (full site, weekly intelligence)
- Advanced: £60k-120k/year (full site + energy + dedicated support)
- Enterprise: £120k+/year (multi-site, bespoke)

CRITICAL: All proposals require Checkpoint 6 founder approval before sharing.
All commercial terms are founder decisions — never prescribe final pricing."""

    def run(self, context: Dict) -> Dict:
        """
        context keys:
          - company: company record
          - pilot: completed pilot record with findings
          - pilot_findings: detailed findings from the pilot
          - contact: primary contact (MD/decision maker)
        """
        company = context.get("company", {})
        pilot = context.get("pilot", {})
        prompt = f"""
Build a commercial proposal and ROI model following this completed diagnostic pilot.

Company:
{company}

Pilot completed:
Type: {pilot.get('pilot_type', '')}
Scope: {pilot.get('scope_description', '')}
Findings: {context.get('pilot_findings', 'Pilot findings not yet documented.')}

Primary contact: {context.get('contact', {{}})}

Subscription tiers: {SUBSCRIPTION_TIERS}

Build the proposal:
{{
  "company_id": "{company.get('company_id', '')}",
  "pilot_id": "{pilot.get('pilot_id', '')}",
  "executive_summary": "...",
  "key_findings": ["..."],
  "roi_model": {{
    "annual_savings_estimate": 0,
    "savings_breakdown": [
      {{
        "category": "...",
        "annual_value": 0,
        "assumption": "...",
        "confidence": "Low|Medium|High"
      }}
    ],
    "payback_period_months": 0,
    "roi_multiple": 0,
    "total_annual_savings": 0,
    "conservative_estimate": true,
    "roi_above_10x_flag": true/false
  }},
  "proposed_package": {{
    "tier": "Starter|Standard|Advanced|Enterprise",
    "scope": "...",
    "arr_suggested_range": "...",
    "rationale": "...",
    "inclusions": ["..."]
  }},
  "implementation_plan": ["..."],
  "next_steps": ["..."],
  "assumptions_register": ["..."],
  "risks": ["..."],
  "checkpoint_6_notes": "...",
  "confidence_level": "Low|Medium|High"
}}

Rules:
- Never finalise pricing — only suggest a range for founder to confirm
- State every assumption clearly
- Flag if ROI multiple exceeds 10x
- Keep executive summary under 200 words
"""
        result = self._call_json(prompt, max_tokens=6000)
        self.crm.log("agent_11_run", {
            "company_id": company.get("company_id"),
            "roi_estimate": result.get("roi_model", {}).get("annual_savings_estimate", 0),
            "roi_flag": result.get("roi_model", {}).get("roi_above_10x_flag", False),
        })
        return result
