"""
Agent 03: Lead Enrichment Agent
Transforms raw leads into rich operational profiles with ICP scoring.
"""
from typing import Dict
from agents.base import BaseAgent
from config import MODEL_VOLUME, SCORE_PRIORITY_A, SCORE_PRIORITY_B


class LeadEnrichmentAgent(BaseAgent):
    name = "Agent 03 - Lead Enrichment"
    model = MODEL_VOLUME
    system_prompt = """You are the Lead Enrichment Agent for Inshira Technologies.

Your role:
- Transform raw lead records into rich operational profiles
- Find decision-maker contacts, financial data, product lines, and operational signals
- Score each enriched lead against ICP criteria (0-100)
- Flag high-fit leads for immediate research escalation

Scoring framework (max 100 points):
- ICP Fit (15): manufacturing type, sector, headcount, location match
- Operational Pain Likelihood (20): evidence of waste, downtime, scrap, poor visibility
- Data Maturity (10): ERP/MES=10, digital systems=7, spreadsheets=4, manual=0
- Pilot Suitability (15): complexity, data readiness, defined process
- Subscription Potential (10): ARR potential based on size and scope
- Urgency (10): active operational pressure signals
- Ability to Pay (10): financial health indicators
- Relationship Warmth (5): existing connections
- Decision-Maker Access (5): ability to reach budget holder
- Strategic Value (+5 bonus): flagship reference potential

Data sources to simulate/use: LinkedIn, Companies House accounts, job postings,
trade press, product catalogues, certifications."""

    def run(self, context: Dict) -> Dict:
        """
        context keys:
          - company: raw company record from CRM
          - icp_criteria: from Agent 01
        """
        company = context.get("company", {})
        prompt = f"""
Enrich the following company record and score it against ICP criteria.

Raw company record:
{company}

ICP criteria:
{context.get('icp_criteria', 'UK manufacturers, 20-500 employees, medium-high complexity.')}

Produce a complete enrichment JSON:
{{
  "company_id": "{company.get('company_id', '')}",
  "enriched_data": {{
    "website": "...",
    "linkedin_url": "...",
    "turnover_band": "<£5m|£5-15m|£15-50m|>£50m",
    "headcount_band": "20-50|51-100|101-250|251-500",
    "products": ["..."],
    "manufacturing_processes": ["..."],
    "customer_base_type": "OEM|Retail|B2B|Mixed",
    "certifications": ["ISO 9001", "..."],
    "energy_intensity": "Low|Medium|High|Very High",
    "operational_complexity": "Low|Medium|High|Very High",
    "data_maturity": "Manual|Basic Digital|ERP|Advanced",
    "recent_news": ["..."],
    "sustainability_commitments": ["..."]
  }},
  "decision_makers": [
    {{
      "first_name": "...",
      "last_name": "...",
      "job_title": "...",
      "persona": "MD|Ops Director|Factory Manager|CI Manager",
      "linkedin_url": "...",
      "decision_maker": true/false,
      "champion": true/false
    }}
  ],
  "icp_score_breakdown": {{
    "icp_fit": 0,
    "operational_pain_likelihood": 0,
    "data_maturity": 0,
    "pilot_suitability": 0,
    "subscription_potential": 0,
    "urgency": 0,
    "ability_to_pay": 0,
    "relationship_warmth": 0,
    "decision_maker_access": 0,
    "strategic_bonus": 0
  }},
  "icp_fit_score": 0,
  "priority_band": "A|B|C|D|Disqualified",
  "data_confidence_score": 0,
  "fast_track_research": true/false,
  "enrichment_notes": "...",
  "pipeline_stage": "Enriched"
}}
"""
        result = self._call_json(prompt, max_tokens=4096)

        # Merge enrichment back into CRM
        company_update = {
            "company_id": company.get("company_id"),
            **result.get("enriched_data", {}),
            "icp_fit_score": result.get("icp_fit_score", 0),
            "pipeline_stage": "Enriched",
        }
        self.crm.upsert_company(company_update)

        # Save decision-maker contacts
        for dm in result.get("decision_makers", []):
            dm["company_id"] = company.get("company_id")
            dm["trust_score"] = 0
            dm["relationship_maturity"] = "Cold"
            self.crm.upsert_contact(dm)

        score = result.get("icp_fit_score", 0)
        self.crm.log("agent_03_run", {
            "company_id": company.get("company_id"),
            "score": score,
            "fast_track": result.get("fast_track_research", False),
        })
        return result
