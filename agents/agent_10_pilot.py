"""
Agent 10: Pilot Structuring Agent
Designs the diagnostic pilot scope for each prospect.
"""
from typing import Dict
from agents.base import BaseAgent
from config import MODEL_COMPLEX


PILOT_LIBRARY = [
    {
        "type": "Manufacturing Efficiency Diagnostic",
        "primary_pain": "Low OEE, hidden downtime, production rate variability",
        "data_required": "Production logs, downtime records, order history",
        "duration_weeks": "4-6",
        "key_deliverable": "Efficiency loss map with root cause analysis and cost estimate",
    },
    {
        "type": "Material Waste Diagnostic",
        "primary_pain": "High scrap rate, material overuse, raw material cost pressure",
        "data_required": "BOM, production records, goods-in/out, scrap logs",
        "duration_weeks": "3-5",
        "key_deliverable": "Material loss waterfall with cost quantification by stage",
    },
    {
        "type": "Energy Hotspot Mapping",
        "primary_pain": "High energy bills, no visibility of energy by process or shift",
        "data_required": "Energy meter data, production schedule, process list",
        "duration_weeks": "3-4",
        "key_deliverable": "Energy hotspot map, shift-level analysis, reduction opportunity estimate",
    },
    {
        "type": "Production Bottleneck Analysis",
        "primary_pain": "Late deliveries, WIP buildup, throughput constraints",
        "data_required": "Production routing, job tracking, delivery data",
        "duration_weeks": "4-5",
        "key_deliverable": "Constraint analysis with throughput improvement model",
    },
    {
        "type": "Scrap and Rework Analysis",
        "primary_pain": "High rework cost, quality escapes, customer returns",
        "data_required": "Quality records, rework logs, inspection data, customer returns",
        "duration_weeks": "3-5",
        "key_deliverable": "Scrap/rework pareto, cost of quality estimate, priority fix list",
    },
    {
        "type": "Process Visibility Assessment",
        "primary_pain": "No KPIs, no real-time data, management by gut feel",
        "data_required": "Available data audit, process map discussion",
        "duration_weeks": "2-3",
        "key_deliverable": "Data maturity scorecard, visibility gap map, priority data capture plan",
    },
    {
        "type": "Operational Loss Quantification",
        "primary_pain": "General suspicion of hidden losses but no clear picture",
        "data_required": "Mixed operational data (whatever is available)",
        "duration_weeks": "5-8",
        "key_deliverable": "Full operational loss model across production stages with total cost estimate",
    },
]


class PilotStructuringAgent(BaseAgent):
    name = "Agent 10 - Pilot Structuring"
    model = MODEL_COMPLEX
    system_prompt = """You are the Pilot Structuring Agent for Inshira Technologies.

Your role:
- Design the diagnostic pilot scope for each prospect
- Create a structured, low-friction entry offer that delivers clear ROI evidence
- The pilot is not a free sample — it is a structured operational intelligence engagement
- Size pilot effort proportionally to deal size

Pilot design principles:
- Select the most relevant pilot type from the library based on discovery findings
- Define exactly what data is needed from the prospect (be specific, not overwhelming)
- Set realistic timelines: most pilots run 3-6 weeks
- KPIs must be measurable from the data the prospect actually has
- Deliverables must be specific findings, not vague 'insights'
- All pilot scopes require Checkpoint 5 approval before sharing with prospect

Data requirement rules:
- Never require more than 3 data sources for a first pilot
- Never scope more than 8 weeks unless strategic account with founder approval
- If data maturity is low: use Process Visibility Assessment first
- Complex data requirements (>3 sources, >8 weeks) escalate to founder"""

    def run(self, context: Dict) -> Dict:
        """
        context keys:
          - company: enriched company record
          - discovery_notes: post-call notes from Agent 09 template
          - hypotheses: validated/partially validated hypotheses from discovery
          - icp_fit_score: lead score
        """
        company = context.get("company", {})
        prompt = f"""
Design a diagnostic pilot scope for this manufacturing prospect.

Company profile:
{company}

Discovery call notes:
{context.get('discovery_notes', 'No discovery notes yet — base on profile and hypotheses.')}

Validated/partially validated hypotheses:
{context.get('hypotheses', [])}

ICP fit score: {context.get('icp_fit_score', 0)}

Available pilot types:
{PILOT_LIBRARY}

Select the most appropriate pilot type and design the full scope:
{{
  "company_id": "{company.get('company_id', '')}",
  "pilot_type": "...",
  "rationale": "...",
  "scope_description": "...",
  "data_sources_required": [
    {{
      "source": "...",
      "format": "...",
      "period_required": "...",
      "acquisition_method": "..."
    }}
  ],
  "kpis": [
    {{
      "kpi_name": "...",
      "measurement_method": "...",
      "baseline_required": true/false
    }}
  ],
  "timeline_weeks": 0,
  "deliverables": ["..."],
  "effort_estimate": "Low|Medium|High",
  "pilot_feasibility_score": 0,
  "data_readiness_assessment": "...",
  "commercial_framing": "...",
  "expected_roi_range": "...",
  "checkpoint_5_notes": "...",
  "complex_data_flag": true/false,
  "status": "Scoping"
}}
"""
        result = self._call_json(prompt, max_tokens=4096)

        # Save pilot record
        pilot_record = {
            "company_id": company.get("company_id"),
            "pilot_type": result.get("pilot_type"),
            "scope_description": result.get("scope_description"),
            "data_sources_required": str(result.get("data_sources_required", [])),
            "kpis": str(result.get("kpis", [])),
            "timeline_weeks": result.get("timeline_weeks"),
            "status": "Scoping",
        }
        saved = self.crm.upsert_pilot(pilot_record)
        result["pilot_id"] = saved.get("pilot_id")

        self.crm.log("agent_10_run", {
            "company_id": company.get("company_id"),
            "pilot_type": result.get("pilot_type"),
            "complex_flag": result.get("complex_data_flag", False),
        })
        return result
