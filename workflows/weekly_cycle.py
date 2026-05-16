"""
Weekly Optimisation Cycle for Inshira Growth OS.
Every Friday: Agent 14 produces the weekly report.
Founder reviews and sets direction for the following week.
"""
from datetime import datetime
from rich.console import Console
from rich.rule import Rule
from rich.panel import Panel
from rich.prompt import Prompt

from memory.crm import CRM
from agents import (
    LearningOptimisationAgent,
    ICPIntelligenceAgent,
    IndustrialTrendAgent,
)
from checkpoints.gates import CheckpointGate

console = Console()


def run_weekly_cycle(crm: CRM = None) -> dict:
    """
    Execute the weekly optimisation cycle.
    Returns the weekly report dict.
    """
    if crm is None:
        crm = CRM()

    gate = CheckpointGate(crm)
    today = datetime.utcnow().strftime("%Y-%m-%d")

    console.print(Rule(f"[bold magenta]Inshira Growth OS — Weekly Review {today}[/bold magenta]"))

    # ------------------------------------------------------------------ #
    # Agent 14: Weekly optimisation report
    # ------------------------------------------------------------------ #
    console.print("\n[cyan]Agent 14: Generating weekly optimisation report...[/cyan]")
    learning_agent = LearningOptimisationAgent(crm)
    weekly_report = learning_agent.run({"period": "weekly"})

    console.print(Panel(
        f"[bold]Overall health:[/bold] {weekly_report.get('overall_health', 'Unknown')}\n"
        f"[bold]Reply rate:[/bold] {weekly_report.get('outreach_performance', {{}}).get('reply_rate_pct', 0):.1f}%\n"
        f"[bold]Positive reply rate:[/bold] {weekly_report.get('outreach_performance', {{}}).get('positive_reply_rate_pct', 0):.1f}%\n"
        f"[bold]Best angle:[/bold] {weekly_report.get('outreach_performance', {{}}).get('best_performing_angle', 'N/A')}\n"
        f"[bold]Bottleneck stage:[/bold] {weekly_report.get('pipeline_velocity', {{}}).get('bottleneck_stage', 'N/A')}",
        title="Weekly Performance Summary",
        border_style="magenta",
    ))

    # Show recommendations
    recs = weekly_report.get("recommendations", [])
    if recs:
        console.print("\n[bold]Recommendations:[/bold]")
        for rec in recs:
            priority_color = "red" if rec.get("priority") == "High" else "yellow"
            console.print(f"  [{priority_color}]{rec.get('priority')}[/{priority_color}] "
                         f"→ {rec.get('agent')}: {rec.get('action')}")

    # Show alerts
    alerts = weekly_report.get("alerts", [])
    if alerts:
        console.print(f"\n[red bold]ALERTS:[/red bold]")
        for alert in alerts:
            console.print(f"  - {alert}")

    # ------------------------------------------------------------------ #
    # Founder review actions
    # ------------------------------------------------------------------ #
    console.print("\n[bold yellow]FOUNDER REVIEW — Please answer the following:[/bold yellow]")

    # 1. ICP adjustment?
    icp_review = Prompt.ask(
        "\n1. Does the sector heatmap suggest ICP priority changes needed?",
        choices=["yes", "no"],
        default="no",
    )
    if icp_review == "yes":
        console.print("[cyan]Running ICP validation check (Checkpoint 1 may be triggered)...[/cyan]")
        icp_agent = ICPIntelligenceAgent(crm)
        icp_result = icp_agent.run({
            "sector_intelligence": str(weekly_report.get("sector_heatmap", [])),
        })
        if icp_result.get("checkpoint_1_required"):
            gate.checkpoint_1_icp_validation(icp_result)

    # 2. Volume target for next week
    volume_target = Prompt.ask(
        "\n2. Outreach volume target for next week (messages to send)",
        default="10",
    )

    # 3. Priority sectors for next week
    priority_sectors = Prompt.ask(
        "\n3. Priority sectors for next week (comma-separated)",
        default="Precision Engineering, Metal Fabrication",
    )

    # 4. Report quality rating
    report_rating = Prompt.ask(
        "\n4. Rate this weekly report quality (1-5)",
        choices=["1", "2", "3", "4", "5"],
        default="4",
    )

    # 5. Any strategic account focus?
    strategic_focus = Prompt.ask(
        "\n5. Any specific strategic account to prioritise this week?",
        default="None",
    )

    # Save weekly review decisions
    crm.log("weekly_review", {
        "date": today,
        "icp_review_triggered": icp_review == "yes",
        "volume_target": volume_target,
        "priority_sectors": priority_sectors,
        "report_rating": report_rating,
        "strategic_focus": strategic_focus,
    })

    console.print(Panel(
        f"Volume target: {volume_target} messages\n"
        f"Priority sectors: {priority_sectors}\n"
        f"Report rating: {report_rating}/5",
        title=f"Week of {today} — Directions Set",
        border_style="green",
    ))

    console.print(Rule("[bold magenta]Weekly Review Complete[/bold magenta]"))
    return weekly_report
