"""
Agent 02: Lead Discovery Agent
Systematically finds high-fit SME manufacturing prospects in the UK.
"""
from typing import Dict, List
from agents.base import BaseAgent
from config import MODEL_VOLUME


class LeadDiscoveryAgent(BaseAgent):
    name = "Agent 02 - Lead Discovery"
    model = MODEL_VOLUME
    system_prompt = """You are the Lead Discovery Agent for Inshira Technologies.

Your role:
- Identify high-fit SME manufacturing prospects in the UK
- Use ICP criteria to filter and prioritise discovery sources
- Deduplicate against existing CRM records
- Generate structured raw lead records ready for enrichment

UK manufacturer discovery sources:
- Companies House (SIC codes: 2561-2562 precision eng, 2410-2599 metal, 2221-2229 plastics,
  1011-1089 food, 2120-2229 pharma, 3030-3099 aerospace, 2910-2932 automotive)
- LinkedIn company search
- Made in Britain directory
- The Manufacturer Top 100
- Thomasnet / Kompass UK

Output must be structured raw lead records. Each lead must have:
company_name, sic_code, estimated_headcount_band, location, primary_manufacturing_type,
discovery_source, and any operational stress or growth signals observed.

Quality over volume. 50-100 genuinely high-fit leads per week is the target."""

    def run(self, context: Dict) -> Dict:
        """
        context keys:
          - icp_criteria: from Agent 01
          - existing_company_ids: list of CRM company IDs to deduplicate
          - target_sectors: list of priority sectors
          - target_regions: list of UK regions to focus on
          - search_query: optional specific search instruction
        """
        existing_ids = context.get("existing_company_ids", [])
        prompt = f"""
You are running lead discovery for Inshira Technologies.

ICP criteria:
{context.get('icp_criteria', 'UK manufacturers, 20-500 employees, medium-high operational complexity.')}

Target sectors (priority order):
{context.get('target_sectors', ['Precision Engineering', 'Metal Fabrication', 'Plastics', 'Food & Beverage'])}

Target regions:
{context.get('target_regions', ['Midlands', 'North West', 'Yorkshire', 'South West'])}

Existing CRM records to deduplicate against (IDs to skip):
{existing_ids[:20] if existing_ids else 'None yet.'}

Search instruction:
{context.get('search_query', 'Run standard ICP-aligned discovery across all target sectors and regions.')}

Generate a list of 10-20 realistic raw lead candidates. For each, produce:
{{
  "raw_leads": [
    {{
      "company_name": "...",
      "companies_house_id": "...",
      "sic_code": "...",
      "sector": "...",
      "manufacturing_type": "...",
      "headcount_band": "20-50|51-100|101-250|251-500",
      "location": "...",
      "discovery_source": "...",
      "operational_signals": ["..."],
      "growth_signals": ["..."],
      "stress_signals": ["..."],
      "notes": "..."
    }}
  ],
  "total_found": 0,
  "deduplication_removed": 0,
  "discovery_summary": "..."
}}
"""
        result = self._call_json(prompt, max_tokens=8192)
        # Save raw leads to CRM
        for lead in result.get("raw_leads", []):
            lead["pipeline_stage"] = "Discovery"
            lead["icp_fit_score"] = 0  # Will be set by Agent 03
            self.crm.upsert_company(lead)
        self.crm.log("agent_02_run", {"leads_found": len(result.get("raw_leads", []))})
        return result
