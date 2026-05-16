"""
Agent 04: Operational Research Agent
Conducts deep operational intelligence research on priority leads.
"""
from typing import Dict
from agents.base import BaseAgent
from config import MODEL_COMPLEX, HIGH_VALUE_ARR_THRESHOLD


class OperationalResearchAgent(BaseAgent):
    name = "Agent 04 - Operational Research"
    model = MODEL_COMPLEX
    system_prompt = """You are the Operational Research Agent for Inshira Technologies.

Your role:
- Conduct deep operational intelligence research on priority manufacturing leads
- Find specific signals of waste, inefficiency, and operational pain before outreach
- Produce an operational intelligence brief that informs pain hypothesis generation

Research dimensions:
1. Financial analysis: margin pressure, working capital stress, growth constraints
2. Job postings analysis: CI Manager, Production Planner, Lean Engineer roles = process pain signal
3. Trade press: operational challenges, expansion plans, capacity issues
4. Product complexity: bespoke, high-mix, custom = higher operational complexity
5. Energy intensity: by sector and process type
6. Operational footprint: sites, shift patterns, certifications
7. Data maturity signals: ERP mentions, tech job postings, digital transformation language

Pain categories to investigate:
- Hidden downtime and OEE losses
- Material waste and scrap by job/process
- Energy cost with no process-level visibility
- Production bottlenecks causing late deliveries
- Rework and quality escapes
- No real-time KPIs or management by gut feel

Flag strategic accounts (>£50k ARR potential) for founder escalation.
Never use sensitive findings (financial distress, redundancies) in outreach without human review."""

    def run(self, context: Dict) -> Dict:
        """
        context keys:
          - company: enriched company record
          - sector_intelligence: from Agent 15
          - icp_criteria: from Agent 01
        """
        company = context.get("company", {})
        prompt = f"""
Conduct deep operational intelligence research on this manufacturing company.

Enriched company profile:
{company}

Sector intelligence:
{context.get('sector_intelligence', 'No specific sector intelligence provided.')}

Produce a comprehensive operational intelligence brief:
{{
  "company_id": "{company.get('company_id', '')}",
  "operational_brief": {{
    "manufacturing_overview": "...",
    "estimated_sites": 1,
    "estimated_shift_patterns": "...",
    "product_complexity": "Low|Medium|High|Very High",
    "primary_operational_risks": ["..."],
    "financial_signals": {{
      "margin_pressure": true/false,
      "working_capital_stress": true/false,
      "growth_constraints": true/false,
      "financial_distress": true/false,
      "notes": "..."
    }},
    "job_posting_signals": ["..."],
    "trade_press_signals": ["..."],
    "technology_signals": ["..."]
  }},
  "pain_signals": [
    {{
      "pain_category": "...",
      "description": "...",
      "evidence": "...",
      "confidence_score": 0,
      "severity": "Low|Medium|High|Critical"
    }}
  ],
  "strategic_account_flag": true/false,
  "estimated_arr_potential": 0,
  "sensitive_findings": [],
  "human_review_required": true/false,
  "review_reason": "...",
  "research_depth_score": 0,
  "pipeline_stage": "Hypothesised"
}}
"""
        result = self._call_json(prompt, max_tokens=4096)

        # Update company in CRM
        if result.get("strategic_account_flag"):
            self.crm.upsert_company({
                "company_id": company.get("company_id"),
                "strategic_flag": True,
                "estimated_arr_potential": result.get("estimated_arr_potential", 0),
            })

        self.crm.log("agent_04_run", {
            "company_id": company.get("company_id"),
            "pain_signals_found": len(result.get("pain_signals", [])),
            "strategic_flag": result.get("strategic_account_flag", False),
        })
        return result
