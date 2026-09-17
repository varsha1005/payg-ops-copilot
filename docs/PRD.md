# PRD v0.2 — PAYG Ops Copilot

## Objective
Help support and field-operations teams turn unstructured messages into correctly routed, action-ready cases with less manual first-pass work.

## Problem statement
Support messages arrive in inconsistent formats. A first responder must extract the issue, judge urgency, identify the owner, decide a safe next step and often write a response. This is repetitive, but fully autonomous handling would be unsafe for payment, identity, fraud, safety and certain service decisions.

## Reviewer-demo principle
The live reviewer demo uses fixed scenarios rather than free-form inputs. This makes testing reproducible: selecting a situation displays the market, channel and message as read-only case context. A production implementation would receive live messages from connected support systems.

## User stories

1. **As a support agent**, I want a clear summary, category and next action so I can handle an incoming case faster.
2. **As a field coordinator**, I want installation/service cases routed with the right context so I can act without rereading long message threads.
3. **As a payment-ops user**, I want payment-related cases flagged for verification so generated text never confirms money movement by itself.
4. **As a product manager**, I want the pilot dashboard to change by case type so I can monitor the metrics and controls that matter for each workflow.

## Functional requirements

### FR1 — Scenario selection for reviewer demo
Provide a set of realistic support situations. When a reviewer selects one, display its market, channel and message as fixed/read-only case details.

### FR2 — Structured triage output
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
- Fraud or safety is suspected
- Customer identity/contact changes are requested
- Payment/access status depends on unverified source data
- Warranty/replacement or repeated-failure decisions need service-history review
- Confidence is below threshold
- Intent is unclear

### FR4 — Scenario-specific pilot dashboard
For the currently selected situation, show:
- Synthetic case count
- Illustrative AI-assist usage
- Human-review requirement
- Primary route
- Case-specific pilot metrics
- Main workflow control/guardrail

Clearly label all prototype numbers as synthetic/illustrative.

### FR5 — Batch processing
Allow CSV upload to triage a backlog and download structured results.

### FR6 — Overall analytics
Retain overall synthetic data/SQL for adoption, overrides, backlog, resolution time, category mix and market/channel analysis.

## Non-functional requirements
- Response target for single-case triage: <5 seconds excluding provider/network latency
- Clear failure state if model API is unavailable
- No secrets committed to repository
- PII minimization
- Auditable decision fields
- Reviewer demo must work without external credentials

## Acceptance criteria

| Scenario | Expected behavior |
|---|---|
| Paid but not reflected | High; Payments / Customer Operations; source-system verification; human review |
| Unlock code invalid | High; verify payment/code status; human review |
| Battery smoke / overheating | Urgent; Safety / Service Operations; immediate human escalation |
| Fake agent / scam concern | Urgent; Risk / Operations; tell customer not to send more money; human review |
| Agent cannot log in | Internal Tools Support; approved recovery path |
| Customer changes phone number | Customer Operations; identity verification before update |
| Missing delivery component | Logistics / Customer Operations; verify order/delivery first |
| Warranty/replacement request | Service Operations; verify service history/policy; human review |
| Repeat product failure | High; review prior visits; human decision on next corrective path |
| Balance query | Low; answer only from verified account data |
| Very unclear message | Other/needs review; ask clarification |
| Model/API fails | Show error and use demo fallback for reviewer continuity |

## Event model for analytics
Suggested events:
- `scenario_selected`
- `triage_requested`
- `triage_completed`
- `triage_failed`
- `suggestion_accepted`
- `suggestion_overridden`
- `ticket_routed`
- `ticket_resolved`
- `ticket_reopened`

Each event should include timestamp, market, channel, issue category, scenario/case type and anonymized user/team identifiers where permitted.
