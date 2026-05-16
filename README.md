# Inshira Growth OS — Multi-Agent B2B Sales Swarm

A 16-agent AI swarm designed to identify, engage, convert, and retain high-fit SME manufacturers in the UK.

## Architecture

| Tier | Agents | Function |
|------|--------|----------|
| Intelligence | 01, 15 | ICP validation and market intelligence |
| Discovery | 02, 03, 04, 05 | Lead finding, enrichment, research, pain hypotheses |
| Engagement | 06, 07, 08, 09 | Relationship intelligence, outreach strategy, messaging, discovery prep |
| Conversion | 10, 11, 12 | Pilot structuring, proposals, subscription expansion |
| Operations | 13, 14, 16 | CRM/memory, learning/optimisation, orchestration |

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create your .env file
cp .env.example .env
# Edit .env — add your ANTHROPIC_API_KEY and FOUNDER_NAME

# 3. Run the daily cycle
python main.py daily
```

## Commands

```bash
python main.py daily          # Full daily automated cycle
python main.py weekly         # Weekly optimisation review (run on Fridays)
python main.py discover       # Lead discovery only
python main.py enrich         # Enrich pending leads
python main.py research <id>  # Deep research a company by CRM ID
python main.py hypotheses <id># Generate pain hypotheses for a company
python main.py strategy <id>  # Design outreach strategy for a company
python main.py message <id>   # Draft outreach message for a company
python main.py pipeline       # Show pipeline summary
python main.py brief          # Show daily brief
python main.py trends         # Sector intelligence scan
```

## Human Approval Gates

Eight mandatory checkpoints — nothing reaches a prospect without founder approval:

| # | Gate | Trigger | SLA |
|---|------|---------|-----|
| 1 | ICP Validation | ICP change proposed | 48 hrs |
| 2 | Lead Shortlist | Enriched batch ready | 24 hrs |
| 3 | Outreach Approval | Message drafted | 24 hrs |
| 4 | Positive Reply | Reply detected | Immediate |
| 5 | Pilot Scope | Pilot brief ready | 48 hrs |
| 6 | Proposal Approval | Proposal drafted | 48 hrs |
| 7 | Subscription Conversion | Prospect ready to buy | Same day |
| 8 | Account Expansion | >£25k expansion identified | 48 hrs |

## Commercial Motion

```
Diagnostic Pilot → ROI Proof → Annual Subscription ARR
```

Entry offer: *"Let us identify what operational losses are costing you."*

## Data

CRM data is stored in `data/*.json` (gitignored). Five memory layers:
- `companies.json` — Company profiles
- `contacts.json` — Relationship tracking
- `outreach.json` — Campaign memory
- `pilots.json` — Pilot records
- `subscriptions.json` — Customer accounts
- `logs.json` — Audit trail

---
*Version 1.0 | Inshira Technologies | Confidential*
