"""
Agent 15: Industrial Trend Monitoring Agent
Monitors UK manufacturing sector news, regulation, energy costs, and policy.
"""
from typing import Dict
from agents.base import BaseAgent
from config import MODEL_VOLUME


class IndustrialTrendAgent(BaseAgent):
    name = "Agent 15 - Industrial Trends"
    model = MODEL_VOLUME
    system_prompt = """You are the Industrial Trend Monitoring Agent for Inshira Technologies.

Your role:
- Monitor UK manufacturing sector news, regulation, energy costs, supply chain pressures, and policy
- Identify emerging pain amplifiers that make Inshira's value proposition more urgent
- Provide strategic intelligence to ICP Agent and Pain Hypothesis Agent

Sources to monitor:
- The Manufacturer (themanufacturer.com)
- Machinery magazine
- Manufacturing Today UK
- The Engineer
- Make UK reports and surveys
- Innovate UK announcements
- UK Government manufacturing policy
- Energy price movements and industrial tariffs
- ETS (Emissions Trading Scheme) changes
- Carbon border adjustment mechanism updates

Pain amplifiers to watch:
- Rising energy costs: strengthens energy hotspot mapping value prop
- Material cost inflation: strengthens waste diagnostic value prop
- Labour cost/availability: strengthens automation and efficiency value prop
- Late delivery penalties: strengthens bottleneck analysis value prop
- ESG/sustainability reporting requirements: strengthens energy tracking value prop
- Brexit supply chain disruption: strengthens operational visibility value prop

Major sector events (trade shows, government reviews, significant announcements)
must be escalated to founder for strategic response planning."""

    def run(self, context: Dict) -> Dict:
        """
        context keys:
          - target_sectors: list of sectors to focus intelligence on
          - previous_brief: last week's intelligence brief
        """
        sectors = context.get("target_sectors",
                              ["Precision Engineering", "Metal Fabrication",
                               "Plastics", "Food & Beverage"])
        prompt = f"""
Produce a weekly UK manufacturing sector intelligence brief for Inshira Technologies.

Target sectors: {sectors}

Previous brief summary: {context.get('previous_brief', 'First brief — no previous context.')}

Produce:
{{
  "week_ending": "...",
  "headline_developments": ["..."],
  "sector_intelligence": [
    {{
      "sector": "...",
      "key_developments": ["..."],
      "pain_amplifiers": ["..."],
      "outreach_timing_signals": ["..."]
    }}
  ],
  "energy_cost_update": {{
    "trend": "Rising|Stable|Falling",
    "uk_industrial_tariff_notes": "...",
    "impact_on_outreach": "..."
  }},
  "regulatory_alerts": ["..."],
  "event_calendar": [
    {{
      "event": "...",
      "date": "...",
      "relevance": "...",
      "outreach_angle": "..."
    }}
  ],
  "emerging_pain_amplifiers": [
    {{
      "amplifier": "...",
      "affected_sectors": ["..."],
      "recommended_outreach_angle_update": "..."
    }}
  ],
  "major_event_flag": true/false,
  "escalation_required": true/false,
  "escalation_reason": "...",
  "intelligence_brief_for_agent_01": "...",
  "intelligence_brief_for_agent_05": "..."
}}
"""
        result = self._call_json(prompt, max_tokens=4096)
        self.crm.log("agent_15_run", {
            "major_event": result.get("major_event_flag", False),
            "escalation": result.get("escalation_required", False),
        })
        return result
