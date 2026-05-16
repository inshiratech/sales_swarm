"""
Agent 05: Manufacturing Pain Hypothesis Agent
Generates specific, credible operational pain hypotheses for each target.
"""
from typing import Dict
from agents.base import BaseAgent
from config import MODEL_COMPLEX


class PainHypothesisAgent(BaseAgent):
    name = "Agent 05 - Pain Hypothesis"
    model = MODEL_COMPLEX
    system_prompt = """You are the Manufacturing Pain Hypothesis Agent for Inshira Technologies.

Your role:
- Generate specific, credible operational pain hypotheses for each target company
- These hypotheses form the intellectual backbone of all outreach
- Each hypothesis must be grounded in: manufacturing type, sector norms, financial signals,
  operational complexity, company size, and growth stage

Pain hypothesis categories:
1. Hidden downtime / OEE losses (production rate below potential, undefined causes)
2. Material waste / scrap (high-mix or bespoke jobs overrunning material budgets)
3. Energy cost visibility (high energy bill, no process-level consumption data)
4. Production bottlenecks (late deliveries, WIP buildup, throughput constraints)
5. Rework and quality escapes (internal rework cost, customer returns)
6. Data and visibility gaps (management by gut feel, no real-time KPIs)
7. Working capital tied in WIP (high complexity, long cycle times)

Hypothesis quality rules:
- Each hypothesis must name a SPECIFIC operational mechanism, not a vague pain
- Each must reference something knowable from public data or sector norms
- Confidence score must reflect actual evidence, not wishful thinking
- Weak hypotheses (<50% confidence) must be flagged for human review

Fast-track to outreach: hypotheses with >85% confidence."""

    def run(self, context: Dict) -> Dict:
        """
        context keys:
          - company: enriched company record
          - operational_brief: from Agent 04
          - pain_signals: from Agent 04
          - sector_pain_patterns: from Agent 14 learning library
        """
        company = context.get("company", {})
        prompt = f"""
Generate 3-5 specific operational pain hypotheses for this manufacturer.

Company profile:
{company}

Operational intelligence brief:
{context.get('operational_brief', {})}

Pain signals identified:
{context.get('pain_signals', [])}

Sector pain patterns (from learning library):
{context.get('sector_pain_patterns', 'No historical patterns yet.')}

Produce:
{{
  "company_id": "{company.get('company_id', '')}",
  "hypotheses": [
    {{
      "rank": 1,
      "pain_category": "...",
      "hypothesis": "...",
      "specific_mechanism": "...",
      "evidence_base": "...",
      "confidence_score": 0,
      "outreach_angle": "...",
      "suggested_subject_line": "...",
      "flag_for_human_review": true/false,
      "fast_track": true/false
    }}
  ],
  "primary_hypothesis_index": 0,
  "overall_confidence": "Low|Medium|High",
  "weak_hypothesis_flag": true/false,
  "notes": "..."
}}

Rules:
- Rank hypotheses from most to least confident
- fast_track = true only if confidence_score > 85
- flag_for_human_review = true if confidence_score < 50
- Each hypothesis must be specific to THIS company, not generic
"""
        result = self._call_json(prompt, max_tokens=4096)

        # Store hypotheses in company record
        if result.get("hypotheses"):
            self.crm.upsert_company({
                "company_id": company.get("company_id"),
                "pain_hypotheses": result.get("hypotheses"),
                "pipeline_stage": "Hypothesised",
            })

        self.crm.log("agent_05_run", {
            "company_id": company.get("company_id"),
            "hypotheses_count": len(result.get("hypotheses", [])),
            "fast_track_count": sum(1 for h in result.get("hypotheses", []) if h.get("fast_track")),
        })
        return result
