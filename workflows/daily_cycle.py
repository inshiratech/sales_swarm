"""
Daily Operating Cycle for Inshira Growth OS.
Runs the automated intelligence chain and produces the daily brief.
"""
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.rule import Rule

from memory.crm import CRM
from agents import (
    ICPIntelligenceAgent,
    LeadDiscoveryAgent,
    LeadEnrichmentAgent,
    OperationalResearchAgent,
    PainHypothesisAgent,
    RelationshipIntelligenceAgent,
    IndustrialTrendAgent,
    FounderVoiceMessagingAgent,
    CRMMemoryAgent,
    WorkflowOrchestrationAgent,
)
from checkpoints.gates import CheckpointGate
from config import SCORE_PRIORITY_B

console = Console()


def run_daily_cycle(crm: Optional[CRM] = None) -> dict:
    """
    Execute the full daily agent cycle:
    1. Sector intelligence (Agent 15)
    2. Lead discovery (Agent 02)
    3. Lead enrichment for new leads (Agent 03)
    4. Relationship decay check (Agent 06)
    5. Daily brief (Agent 16)
    6. Present pending outreach for approval (Checkpoint 3)

    Returns the daily brief dict.
    """
    if crm is None:
        crm = CRM()

    gate = CheckpointGate(crm)
    today = datetime.utcnow().strftime("%Y-%m-%d")

    console.print(Rule(f"[bold blue]Inshira Growth OS — Daily Cycle {today}[/bold blue]"))

    # ------------------------------------------------------------------ #
    # Step 1: Industrial trend monitoring (Agent 15)
    # ------------------------------------------------------------------ #
    console.print("\n[cyan]Agent 15: Scanning sector intelligence...[/cyan]")
    trends_agent = IndustrialTrendAgent(crm)
    sector_intel = trends_agent.run({
        "target_sectors": ["Precision Engineering", "Metal Fabrication",
                           "Plastics", "Food & Beverage"],
    })
    console.print(f"  Headlines: {sector_intel.get('headline_developments', [])[:2]}")
    if sector_intel.get("escalation_required"):
        console.print(f"  [red]ESCALATION: {sector_intel.get('escalation_reason')}[/red]")

    # ------------------------------------------------------------------ #
    # Step 2: Lead discovery (Agent 02)
    # ------------------------------------------------------------------ #
    console.print("\n[cyan]Agent 02: Running lead discovery...[/cyan]")
    existing_ids = [c.get("company_id") for c in crm.all_companies()]
    discovery_agent = LeadDiscoveryAgent(crm)
    discovery_result = discovery_agent.run({
        "icp_criteria": "UK manufacturers, 20-500 employees, medium-high complexity",
        "existing_company_ids": existing_ids,
        "target_sectors": ["Precision Engineering", "Metal Fabrication"],
        "target_regions": ["Midlands", "North West", "Yorkshire"],
    })
    new_leads = discovery_result.get("raw_leads", [])
    console.print(f"  New leads found: {len(new_leads)}")

    # ------------------------------------------------------------------ #
    # Step 3: Enrich new leads (Agent 03)
    # ------------------------------------------------------------------ #
    unenriched = [c for c in crm.all_companies()
                  if c.get("pipeline_stage") == "Discovery"][:5]  # Process up to 5 per day

    if unenriched:
        console.print(f"\n[cyan]Agent 03: Enriching {len(unenriched)} leads...[/cyan]")
        enrichment_agent = LeadEnrichmentAgent(crm)
        enriched_count = 0
        for company in unenriched:
            result = enrichment_agent.run({
                "company": company,
                "icp_criteria": "UK manufacturers, 20-500 employees, medium-high complexity",
            })
            score = result.get("icp_fit_score", 0)
            console.print(f"  {company.get('company_name', 'Unknown')}: Score {score} "
                         f"({result.get('priority_band', '?')})")
            enriched_count += 1
        console.print(f"  Enriched: {enriched_count} leads")

    # ------------------------------------------------------------------ #
    # Step 4: Check for pending outreach approvals (Checkpoint 3)
    # ------------------------------------------------------------------ #
    pending = crm.outreach_pending_approval()
    if pending:
        console.print(f"\n[yellow]Checkpoint 3: {len(pending)} messages pending approval[/yellow]")
        for outreach in pending[:5]:  # Show up to 5 at a time
            company = crm.get_company(outreach.get("company_id", ""))
            company_name = company.get("company_name", "Unknown") if company else "Unknown"
            hypotheses = company.get("pain_hypotheses", [{}]) if company else [{}]
            top_h = hypotheses[0].get("pain_category", "") if hypotheses else ""
            strategic = company.get("strategic_flag", False) if company else False

            decision = gate.checkpoint_3_outreach_approval(
                outreach_id=outreach.get("outreach_id", ""),
                company_name=company_name,
                subject=outreach.get("subject_line", ""),
                message_body=outreach.get("message_draft", ""),
                hypothesis=top_h,
                touch_number=outreach.get("touch_number", 1),
                strategic=strategic,
            )

    # ------------------------------------------------------------------ #
    # Step 5: CRM health check (Agent 13)
    # ------------------------------------------------------------------ #
    console.print("\n[cyan]Agent 13: CRM health check...[/cyan]")
    crm_agent = CRMMemoryAgent(crm)
    crm_report = crm_agent.run({})
    console.print(f"  Data quality score: {crm_report.get('data_quality_score', 0)}")
    if crm_report.get("stale_record_count", 0) > 0:
        console.print(f"  [yellow]Stale records: {crm_report.get('stale_record_count')}[/yellow]")

    # ------------------------------------------------------------------ #
    # Step 6: Daily brief (Agent 16)
    # ------------------------------------------------------------------ #
    console.print("\n[cyan]Agent 16: Compiling daily brief...[/cyan]")
    orch_agent = WorkflowOrchestrationAgent(crm)
    daily_brief = orch_agent.run({"date": today})

    console.print("\n")
    console.print(Rule("[bold green]DAILY BRIEF[/bold green]"))
    console.print(f"[bold]Priority:[/bold] {daily_brief.get('recommended_focus', '')}")
    console.print(f"[bold]Estimated founder time:[/bold] "
                 f"{daily_brief.get('estimated_founder_time_required_minutes', 0)} minutes")

    escalations = daily_brief.get("immediate_escalations", [])
    if escalations:
        console.print(f"\n[red bold]IMMEDIATE ESCALATIONS ({len(escalations)}):[/red bold]")
        for e in escalations:
            console.print(f"  - {e.get('type')}: {e.get('recommended_action')}")

    console.print(f"\n[bold]Pipeline:[/bold]")
    for stage, count in daily_brief.get("pipeline_movement", {}).items():
        console.print(f"  {stage}: {count}")

    console.print(Rule("[bold blue]Daily Cycle Complete[/bold blue]"))
    return daily_brief
