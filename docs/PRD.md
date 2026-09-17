# PRD v0.1 — PAYG Ops Copilot

## Objective
Help support and field-operations teams turn unstructured messages into correctly routed, action-ready support tickets with less manual effort.

## Problem statement
Support messages arrive in inconsistent formats. The first responder must manually extract the issue, judge urgency, identify the owner, decide a safe next step and write a response. This is repetitive and slows down resolution, but fully autonomous handling would be unsafe for payment, identity and fraud cases.

## User stories

1. **As a support agent**, I want a clear summary, category and next action so I can handle an incoming case faster.
2. **As a field coordinator**, I want installation/service cases routed with the right context so I can follow up without rereading long message threads.
3. **As a payment-ops user**, I want payment-related cases to be flagged for verification so the system never tells a customer that money was received without checking the ledger.
4. **As a product manager**, I want usage, overrides and resolution metrics so I can understand whether the copilot is helping.

## Functional requirements

### FR1 — Message intake
Accept a message plus market and channel.

### FR2 — Structured output
Return:
- Summary
- Category
- Priority
- Owner team
- Recommended next action
- Draft response
- Confidence
- Human-review flag
- Reason

### FR3 — Guardrails
Always require human review when:
- Fraud/safety is suspected
- Customer identity/contact changes are requested
- Payment/access status depends on unverified source data
- Confidence is below threshold
- Intent is unclear

### FR4 — Batch processing
Allow CSV upload to triage a backlog and download results.

### FR5 — Analytics
Show:
- AI usage rate
- Human override rate
- Open backlog
- High/urgent count
- Average resolution time
- Distribution by category and market

## Non-functional requirements
- Response target for single-message triage: <5 seconds excluding provider/network latency
- Clear failure state if model API is unavailable
- No secrets committed to repository
- PII minimization
- Auditable decision fields

## Acceptance criteria

| Scenario | Expected behavior |
|---|---|
| Paid but not reflected | Category = Payment not reflected; High; human review |
| Unlock code invalid | Unlock code issue; High; payment/code verification action |
| Agent cannot log in | Agent app/access issue; Internal Tools Support |
| Customer changes phone number | Human review before account update |
| Fraud/cash concern | Urgent; Risk/Operations; human review |
| Very unclear message | Other/needs review; ask clarification |
| Model/API fails | Show error and use demo fallback for reviewer continuity |

## Event model for analytics
Suggested events:
- `triage_requested`
- `triage_completed`
- `triage_failed`
- `suggestion_accepted`
- `suggestion_overridden`
- `ticket_routed`
- `ticket_resolved`
- `ticket_reopened`

Each event should include timestamp, market, channel, issue category and anonymized user/team identifiers where permitted.
