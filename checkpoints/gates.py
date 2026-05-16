"""
Inshira Growth OS - Human Approval Checkpoint Gates
Eight mandatory approval gates. No gate can be bypassed.
Agent 16 enforces compliance and flags any violations.
"""
from datetime import datetime
from typing import Any, Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm
from memory.crm import CRM

console = Console()


class CheckpointGate:
    """
    Presents information to the human and collects an approval decision.
    All decisions are logged to the CRM audit trail.
    """

    CHECKPOINTS = {
        1: ("ICP Validation",          "Founder",           "48 hours"),
        2: ("Lead Shortlist Review",   "Commercial Lead",   "24 hours"),
        3: ("Outreach Approval",       "Founder/Comm Lead", "24 hours"),
        4: ("Positive Reply",          "Founder",           "Immediate"),
        5: ("Pilot Scope Approval",    "Founder",           "48 hours"),
        6: ("Proposal Approval",       "Founder",           "48 hours"),
        7: ("Subscription Conversion", "Founder",           "Same Day"),
        8: ("Account Expansion",       "Founder",           "48 hours"),
    }

    def __init__(self, crm: CRM):
        self.crm = crm

    def _header(self, gate_number: int) -> None:
        name, owner, sla = self.CHECKPOINTS[gate_number]
        console.print(Panel(
            f"[bold red]CHECKPOINT {gate_number}[/bold red]: [bold]{name}[/bold]\n"
            f"Presented to: [yellow]{owner}[/yellow]   |   SLA: [cyan]{sla}[/cyan]",
            style="bold white on blue",
        ))

    def _log_decision(self, gate: int, decision: str, payload: Dict,
                      notes: str = "", approver: str = "Founder") -> None:
        self.crm.log(f"checkpoint_{gate}_decision", {
            "gate": gate,
            "gate_name": self.CHECKPOINTS[gate][0],
            "decision": decision,
            "approver": approver,
            "notes": notes,
            "timestamp": datetime.utcnow().isoformat(),
            "payload_summary": {k: str(v)[:100] for k, v in payload.items()},
        })

    # ------------------------------------------------------------------ #
    # Checkpoint 1: ICP Validation
    # ------------------------------------------------------------------ #
    def checkpoint_1_icp_validation(self, icp_report: Dict) -> str:
        self._header(1)
        console.print("[bold]Proposed ICP changes:[/bold]")
        console.print(f"Summary: {icp_report.get('icp_summary', 'N/A')}")
        console.print(f"Change rationale: {icp_report.get('change_rationale', 'N/A')}")
        console.print(f"Material change: {icp_report.get('material_change_detected', False)}")
        console.print(f"Sector priorities: {icp_report.get('sector_priorities', [])}")

        decision = Prompt.ask(
            "\nDecision",
            choices=["approve", "revise", "reject"],
            default="approve",
        )
        notes = Prompt.ask("Notes (optional)", default="")
        self._log_decision(1, decision, icp_report, notes)
        console.print(f"[green]Checkpoint 1 recorded: {decision.upper()}[/green]\n")
        return decision

    # ------------------------------------------------------------------ #
    # Checkpoint 2: Lead Shortlist Review
    # ------------------------------------------------------------------ #
    def checkpoint_2_lead_shortlist(self, leads: list) -> Dict:
        self._header(2)
        table = Table(title=f"Lead Shortlist ({len(leads)} leads)")
        table.add_column("Company", style="cyan")
        table.add_column("Sector")
        table.add_column("Score", justify="right", style="green")
        table.add_column("Priority Band")
        table.add_column("Top Hypothesis")

        for lead in leads[:20]:
            table.add_row(
                lead.get("company_name", "Unknown"),
                lead.get("sector", ""),
                str(lead.get("icp_fit_score", 0)),
                lead.get("priority_band", ""),
                str(lead.get("pain_hypotheses", [{}])[0].get("pain_category", ""))
                if lead.get("pain_hypotheses") else "",
            )
        console.print(table)

        approved_ids = []
        disqualified_ids = []
        strategic_ids = []

        for lead in leads:
            console.print(f"\n[bold]{lead.get('company_name')}[/bold] "
                         f"(Score: {lead.get('icp_fit_score', 0)})")
            action = Prompt.ask(
                "  Action",
                choices=["approve", "disqualify", "strategic", "skip"],
                default="approve",
            )
            if action == "approve":
                approved_ids.append(lead.get("company_id"))
            elif action == "disqualify":
                disqualified_ids.append(lead.get("company_id"))
            elif action == "strategic":
                strategic_ids.append(lead.get("company_id"))
                approved_ids.append(lead.get("company_id"))

        result = {
            "approved": approved_ids,
            "disqualified": disqualified_ids,
            "strategic": strategic_ids,
        }
        notes = Prompt.ask("General notes (optional)", default="")
        self._log_decision(2, "mixed", {"lead_count": len(leads)}, notes)

        # Update CRM
        for cid in disqualified_ids:
            self.crm.update_company_stage(cid, "Disqualified")
        for cid in strategic_ids:
            self.crm.upsert_company({"company_id": cid, "strategic_flag": True})

        console.print(f"[green]Checkpoint 2 complete. Approved: {len(approved_ids)}, "
                     f"Disqualified: {len(disqualified_ids)}, Strategic: {len(strategic_ids)}[/green]\n")
        return result

    # ------------------------------------------------------------------ #
    # Checkpoint 3: Outreach Approval
    # ------------------------------------------------------------------ #
    def checkpoint_3_outreach_approval(self, outreach_id: str,
                                        company_name: str,
                                        subject: str,
                                        message_body: str,
                                        hypothesis: str,
                                        touch_number: int,
                                        strategic: bool = False) -> str:
        self._header(3)
        if strategic:
            console.print("[bold red]STRATEGIC ACCOUNT — Founder personal review required[/bold red]")

        console.print(Panel(
            f"[bold]Company:[/bold] {company_name}\n"
            f"[bold]Touch:[/bold] {touch_number}\n"
            f"[bold]Hypothesis:[/bold] {hypothesis}\n\n"
            f"[bold]Subject:[/bold] {subject}\n\n"
            f"{message_body}",
            title="Draft Message",
            border_style="yellow",
        ))

        decision = Prompt.ask(
            "\nDecision",
            choices=["approve", "revise", "reject", "hold"],
            default="approve",
        )
        notes = Prompt.ask("Revision notes / reason (optional)", default="")

        if decision == "approve":
            self.crm.approve_outreach(outreach_id, "Founder")
            console.print(f"[green]Message APPROVED for {company_name}[/green]\n")
        else:
            self.crm.reject_outreach(outreach_id, notes)
            console.print(f"[yellow]Message {decision.upper()} for {company_name}[/yellow]\n")

        self._log_decision(3, decision, {"outreach_id": outreach_id, "company": company_name}, notes)
        return decision

    # ------------------------------------------------------------------ #
    # Checkpoint 4: Positive Reply Escalation
    # ------------------------------------------------------------------ #
    def checkpoint_4_positive_reply(self, company_name: str, contact_name: str,
                                     reply_content: str, context_brief: str) -> str:
        self._header(4)
        console.print(Panel(
            f"[bold red]POSITIVE REPLY DETECTED[/bold red]\n\n"
            f"[bold]Company:[/bold] {company_name}\n"
            f"[bold]Contact:[/bold] {contact_name}\n\n"
            f"[bold]Reply:[/bold]\n{reply_content}\n\n"
            f"[bold]Context:[/bold] {context_brief}",
            title="ACTION REQUIRED — Respond within 4 business hours",
            border_style="red",
        ))

        decision = Prompt.ask(
            "\nAction",
            choices=["respond_personally", "delegate_response", "book_meeting"],
            default="respond_personally",
        )
        notes = Prompt.ask("Notes / next steps", default="")
        self._log_decision(4, decision, {"company": company_name, "contact": contact_name}, notes)
        console.print(f"[green]Checkpoint 4 recorded: {decision.upper()}[/green]\n")
        return decision

    # ------------------------------------------------------------------ #
    # Checkpoint 5: Pilot Scope Approval
    # ------------------------------------------------------------------ #
    def checkpoint_5_pilot_scope(self, pilot_brief: Dict, company_name: str) -> str:
        self._header(5)
        console.print(Panel(
            f"[bold]Company:[/bold] {company_name}\n"
            f"[bold]Pilot type:[/bold] {pilot_brief.get('pilot_type', '')}\n"
            f"[bold]Timeline:[/bold] {pilot_brief.get('timeline_weeks', '')} weeks\n"
            f"[bold]Effort:[/bold] {pilot_brief.get('effort_estimate', '')}\n"
            f"[bold]Scope:[/bold] {pilot_brief.get('scope_description', '')}\n"
            f"[bold]Data required:[/bold] {pilot_brief.get('data_sources_required', '')}\n"
            f"[bold]Commercial framing:[/bold] {pilot_brief.get('commercial_framing', '')}\n"
            f"[bold]Expected ROI range:[/bold] {pilot_brief.get('expected_roi_range', '')}",
            title="Pilot Brief — Review Before Sharing with Prospect",
            border_style="cyan",
        ))

        decision = Prompt.ask(
            "\nDecision",
            choices=["approve", "revise", "hold"],
            default="approve",
        )
        notes = Prompt.ask("Notes / revisions required (optional)", default="")
        self._log_decision(5, decision, pilot_brief, notes)
        console.print(f"[green]Checkpoint 5 recorded: {decision.upper()}[/green]\n")
        return decision

    # ------------------------------------------------------------------ #
    # Checkpoint 6: Proposal Approval
    # ------------------------------------------------------------------ #
    def checkpoint_6_proposal_approval(self, proposal: Dict, company_name: str) -> str:
        self._header(6)
        roi = proposal.get("roi_model", {})
        console.print(Panel(
            f"[bold]Company:[/bold] {company_name}\n"
            f"[bold]Annual savings estimate:[/bold] £{roi.get('annual_savings_estimate', 0):,}\n"
            f"[bold]ROI multiple:[/bold] {roi.get('roi_multiple', 0)}x\n"
            f"[bold]Payback period:[/bold] {roi.get('payback_period_months', 0)} months\n"
            f"[bold]10x flag:[/bold] {roi.get('roi_above_10x_flag', False)}\n"
            f"[bold]Proposed tier:[/bold] {proposal.get('proposed_package', {{}}).get('tier', '')}\n"
            f"[bold]Suggested ARR range:[/bold] {proposal.get('proposed_package', {{}}).get('arr_suggested_range', '')}\n\n"
            f"[bold]Executive summary:[/bold]\n{proposal.get('executive_summary', '')}",
            title="CRITICAL: Review all ROI claims before approving",
            border_style="red",
        ))

        if roi.get("roi_above_10x_flag"):
            console.print("[bold red]WARNING: ROI claim exceeds 10x — requires additional evidence[/bold red]")

        decision = Prompt.ask(
            "\nDecision",
            choices=["approve", "revise_roi", "revise_pricing", "hold"],
            default="approve",
        )
        notes = Prompt.ask("Notes / required revisions", default="")
        self._log_decision(6, decision, {"company": company_name,
                                          "roi": roi.get("annual_savings_estimate", 0)}, notes)
        console.print(f"[green]Checkpoint 6 recorded: {decision.upper()}[/green]\n")
        return decision

    # ------------------------------------------------------------------ #
    # Checkpoint 7: Subscription Conversion
    # ------------------------------------------------------------------ #
    def checkpoint_7_conversion(self, conversion_brief: Dict, company_name: str) -> str:
        self._header(7)
        console.print(Panel(
            f"[bold]Company:[/bold] {company_name}\n"
            f"[bold]Context:[/bold] {conversion_brief.get('context', '')}\n"
            f"[bold]Proposed terms:[/bold] {conversion_brief.get('proposed_terms', '')}\n"
            f"[bold]Objections raised:[/bold] {conversion_brief.get('objections', [])}",
            title="Subscription Conversion — Founder-Led Commercial Discussion",
            border_style="green",
        ))

        console.print("[bold]This is a founder-led commercial discussion. No agent should be "
                     "involved in the negotiation.[/bold]")
        decision = Prompt.ask("\nOutcome", choices=["converted", "follow_up", "lost"], default="follow_up")
        arr_value = 0
        if decision == "converted":
            arr_str = Prompt.ask("ARR value agreed (£)", default="0")
            try:
                arr_value = int(arr_str.replace(",", "").replace("£", ""))
            except ValueError:
                arr_value = 0
            # Create subscription record
            self.crm.upsert_subscription({
                "company_id": conversion_brief.get("company_id", ""),
                "arr_value": arr_value,
                "account_health_score": 80,
                "renewal_risk": "Low",
            })
            self.crm.update_company_stage(conversion_brief.get("company_id", ""), "Customer")

        notes = Prompt.ask("Notes", default="")
        self._log_decision(7, decision, {"company": company_name, "arr": arr_value}, notes)
        console.print(f"[green]Checkpoint 7 recorded: {decision.upper()}[/green]\n")
        return decision

    # ------------------------------------------------------------------ #
    # Checkpoint 8: Strategic Account Expansion
    # ------------------------------------------------------------------ #
    def checkpoint_8_expansion(self, expansion_brief: Dict, company_name: str) -> str:
        self._header(8)
        console.print(Panel(
            f"[bold]Company:[/bold] {company_name}\n"
            f"[bold]Current ARR:[/bold] £{expansion_brief.get('current_arr', 0):,}\n"
            f"[bold]Expansion opportunity:[/bold] {expansion_brief.get('description', '')}\n"
            f"[bold]Estimated additional ARR:[/bold] £{expansion_brief.get('expansion_arr_estimate', 0):,}\n"
            f"[bold]Readiness:[/bold] {expansion_brief.get('readiness', '')}",
            title="Account Expansion Opportunity (>£25k ARR)",
            border_style="magenta",
        ))

        decision = Prompt.ask(
            "\nDecision",
            choices=["approve_approach", "revise", "hold_for_renewal"],
            default="approve_approach",
        )
        notes = Prompt.ask("Notes / direction", default="")
        self._log_decision(8, decision, expansion_brief, notes)
        console.print(f"[green]Checkpoint 8 recorded: {decision.upper()}[/green]\n")
        return decision
