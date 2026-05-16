"""
Inshira Growth OS — Main Entry Point
Multi-Agent B2B Sales Swarm for UK SME Manufacturers

Usage:
  python main.py daily          # Run the daily cycle
  python main.py weekly         # Run the weekly optimisation review
  python main.py discover       # Run lead discovery only
  python main.py enrich         # Enrich pending leads
  python main.py research <id>  # Deep research a specific company
  python main.py hypotheses <id># Generate pain hypotheses for a company
  python main.py strategy <id>  # Design outreach strategy for a company
  python main.py message <id>   # Draft outreach messages for a company
  python main.py pipeline       # Show pipeline summary
  python main.py brief          # Show daily brief only (no auto-run)
  python main.py trends         # Run sector intelligence update
"""
import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from memory.crm import CRM
from workflows.daily_cycle import run_daily_cycle
from workflows.weekly_cycle import run_weekly_cycle
from agents import (
    LeadDiscoveryAgent,
    LeadEnrichmentAgent,
    OperationalResearchAgent,
    PainHypothesisAgent,
    OutreachStrategyAgent,
    FounderVoiceMessagingAgent,
    WorkflowOrchestrationAgent,
    IndustrialTrendAgent,
)
from checkpoints.gates import CheckpointGate

console = Console()
crm = CRM()


def cmd_pipeline():
    """Show current pipeline summary."""
    summary = crm.pipeline_summary()
    companies = crm.all_companies()

    table = Table(title="Inshira Growth OS — Pipeline Summary")
    table.add_column("Stage", style="cyan")
    table.add_column("Count", justify="right", style="green")

    for stage, count in sorted(summary.items(), key=lambda x: x[0]):
        table.add_row(stage, str(count))
    table.add_row("[bold]TOTAL[/bold]", f"[bold]{len(companies)}[/bold]")

    console.print(table)

    # Show high-fit leads
    high_fit = crm.companies_above_score(70)
    if high_fit:
        console.print(f"\n[bold yellow]High-fit leads (score 70+): {len(high_fit)}[/bold yellow]")
        for c in high_fit[:10]:
            console.print(f"  {c.get('company_name')} — Score: {c.get('icp_fit_score')} "
                         f"({'STRATEGIC' if c.get('strategic_flag') else c.get('priority_band', '')})")


def cmd_discover():
    """Run lead discovery."""
    console.print("[cyan]Running lead discovery...[/cyan]")
    agent = LeadDiscoveryAgent(crm)
    result = agent.run({
        "icp_criteria": "UK manufacturers, 20-500 employees, medium-high complexity",
        "existing_company_ids": [c.get("company_id") for c in crm.all_companies()],
        "target_sectors": ["Precision Engineering", "Metal Fabrication", "Plastics"],
        "target_regions": ["Midlands", "North West", "Yorkshire", "South West"],
    })
    leads = result.get("raw_leads", [])
    console.print(f"[green]Discovered {len(leads)} new leads[/green]")
    for lead in leads:
        console.print(f"  + {lead.get('company_name')} ({lead.get('sector')}) — {lead.get('location')}")


def cmd_enrich():
    """Enrich all unenriched leads."""
    unenriched = [c for c in crm.all_companies() if c.get("pipeline_stage") == "Discovery"]
    if not unenriched:
        console.print("[yellow]No leads pending enrichment.[/yellow]")
        return
    console.print(f"[cyan]Enriching {len(unenriched)} leads...[/cyan]")
    agent = LeadEnrichmentAgent(crm)
    for company in unenriched:
        result = agent.run({"company": company, "icp_criteria": ""})
        console.print(f"  {company.get('company_name')}: Score {result.get('icp_fit_score', 0)} "
                     f"— {result.get('priority_band', '?')}")


def cmd_research(company_id: str):
    """Deep research a specific company (Agent 04)."""
    company = crm.get_company(company_id)
    if not company:
        console.print(f"[red]Company {company_id} not found in CRM[/red]")
        return
    console.print(f"[cyan]Running deep research on {company.get('company_name')}...[/cyan]")
    agent = OperationalResearchAgent(crm)
    result = agent.run({"company": company})
    pain_signals = result.get("pain_signals", [])
    console.print(f"[green]Research complete. Pain signals found: {len(pain_signals)}[/green]")
    for signal in pain_signals:
        console.print(f"  [{signal.get('confidence_score', 0)}%] {signal.get('pain_category')}: "
                     f"{signal.get('description')[:80]}")
    if result.get("strategic_account_flag"):
        console.print(f"[bold red]STRATEGIC ACCOUNT FLAG — Est. ARR: "
                     f"£{result.get('estimated_arr_potential', 0):,}[/bold red]")


def cmd_hypotheses(company_id: str):
    """Generate pain hypotheses for a company (Agent 05)."""
    company = crm.get_company(company_id)
    if not company:
        console.print(f"[red]Company {company_id} not found[/red]")
        return
    console.print(f"[cyan]Generating pain hypotheses for {company.get('company_name')}...[/cyan]")
    agent = PainHypothesisAgent(crm)
    result = agent.run({
        "company": company,
        "operational_brief": {},
        "pain_signals": [],
    })
    hypotheses = result.get("hypotheses", [])
    console.print(f"[green]Generated {len(hypotheses)} hypotheses[/green]")
    for h in hypotheses:
        ft = " [FAST TRACK]" if h.get("fast_track") else ""
        console.print(f"  [{h.get('confidence_score', 0)}%]{ft} {h.get('pain_category')}: "
                     f"{h.get('hypothesis')[:80]}")


def cmd_strategy(company_id: str):
    """Design outreach strategy for a company (Agent 07)."""
    company = crm.get_company(company_id)
    if not company:
        console.print(f"[red]Company {company_id} not found[/red]")
        return
    console.print(f"[cyan]Designing outreach strategy for {company.get('company_name')}...[/cyan]")
    agent = OutreachStrategyAgent(crm)
    hypotheses = company.get("pain_hypotheses", [])
    result = agent.run({
        "company": company,
        "hypotheses": hypotheses,
        "priority_band": company.get("priority_band", "B"),
    })
    console.print(f"[green]Strategy designed: {result.get('sequence_name')}[/green]")
    for touch in result.get("touches", []):
        console.print(f"  Touch {touch.get('touch_number')} — Day {touch.get('send_day')} "
                     f"via {touch.get('channel')}: {touch.get('outreach_angle')}")


def cmd_message(company_id: str):
    """Draft outreach messages for a company (Agent 08)."""
    company = crm.get_company(company_id)
    if not company:
        console.print(f"[red]Company {company_id} not found[/red]")
        return
    contacts = crm.contacts_for_company(company_id)
    if not contacts:
        console.print(f"[yellow]No contacts found for {company.get('company_name')}. "
                     f"Run enrichment first.[/yellow]")
        return
    primary_contact = next((c for c in contacts if c.get("decision_maker")), contacts[0])
    hypotheses = company.get("pain_hypotheses", [{}])
    primary_h = hypotheses[0] if hypotheses else {}

    console.print(f"[cyan]Drafting message for {company.get('company_name')} — "
                 f"{primary_contact.get('first_name')} {primary_contact.get('last_name')}...[/cyan]")
    agent = FounderVoiceMessagingAgent(crm)
    result = agent.run({
        "company": company,
        "contact": primary_contact,
        "hypothesis": primary_h,
        "touch_number": 1,
        "channel": "Email",
        "outreach_angle": primary_h.get("outreach_angle", ""),
    })

    console.print(Panel(
        f"[bold]Subject:[/bold] {result.get('subject_line', '')}\n\n"
        f"{result.get('message_body', '')}",
        title=f"Draft Message — {company.get('company_name')} (PENDING APPROVAL)",
        border_style="yellow",
    ))
    console.print(f"[dim]Word count: {result.get('word_count', 0)} | "
                 f"Confidence: {result.get('confidence_score', 0)}%[/dim]")
    console.print("[bold]→ Review and approve via daily cycle (Checkpoint 3)[/bold]")


def cmd_trends():
    """Run sector intelligence update (Agent 15)."""
    console.print("[cyan]Running sector intelligence scan...[/cyan]")
    agent = IndustrialTrendAgent(crm)
    result = agent.run({"target_sectors": ["Precision Engineering", "Metal Fabrication",
                                            "Plastics", "Food & Beverage"]})
    console.print("[green]Intelligence brief produced:[/green]")
    for headline in result.get("headline_developments", []):
        console.print(f"  • {headline}")
    amplifiers = result.get("emerging_pain_amplifiers", [])
    if amplifiers:
        console.print("\n[yellow]Emerging pain amplifiers:[/yellow]")
        for amp in amplifiers:
            console.print(f"  → {amp.get('amplifier')}")


def cmd_brief():
    """Show current daily brief."""
    agent = WorkflowOrchestrationAgent(crm)
    brief = agent.run({"date": datetime.utcnow().strftime("%Y-%m-%d")})
    console.print(Panel(
        f"Priority: {brief.get('recommended_focus', '')}\n"
        f"Pending approvals: {brief.get('outreach_approvals_pending', 0)}\n"
        f"Positive replies: {brief.get('positive_replies_requiring_response', 0)}\n"
        f"High-fit leads: {brief.get('new_high_fit_leads', 0)}\n"
        f"At-risk subscriptions: {brief.get('at_risk_subscriptions', 0)}\n"
        f"Est. time required: {brief.get('estimated_founder_time_required_minutes', 0)} min",
        title="Daily Brief",
        border_style="blue",
    ))


def main():
    args = sys.argv[1:]
    if not args:
        console.print(__doc__)
        return

    cmd = args[0].lower()

    if cmd == "daily":
        run_daily_cycle(crm)
    elif cmd == "weekly":
        run_weekly_cycle(crm)
    elif cmd == "discover":
        cmd_discover()
    elif cmd == "enrich":
        cmd_enrich()
    elif cmd == "research" and len(args) > 1:
        cmd_research(args[1])
    elif cmd == "hypotheses" and len(args) > 1:
        cmd_hypotheses(args[1])
    elif cmd == "strategy" and len(args) > 1:
        cmd_strategy(args[1])
    elif cmd == "message" and len(args) > 1:
        cmd_message(args[1])
    elif cmd == "pipeline":
        cmd_pipeline()
    elif cmd == "brief":
        cmd_brief()
    elif cmd == "trends":
        cmd_trends()
    else:
        console.print(f"[red]Unknown command: {cmd}[/red]")
        console.print(__doc__)


if __name__ == "__main__":
    main()
