# PAYG Ops Copilot

**AI-first support triage and operations analytics prototype**  
Built as an independent case study for an Associate Product Manager — Digitization & Automation role.  
**Candidate:** Varsha Panguluri

**Live demo:** https://varsha1005.github.io/payg-ops-copilot/  
**GitHub repository:** https://github.com/varsha1005/payg-ops-copilot

> This project uses synthetic data only and is not an official Sun King product. Assumptions about internal workflows are hypotheses based on public information and the role description.

## The problem

PAYG solar operations combine recurring payments, field service, customer support and internal agent workflows. Public Sun King information explains that EasyBuy customers can pay through mobile money or cash and receive codes that keep products active. A large field-agent/service network makes fast, consistent issue handling important.

Support messages can cover payment failures, unlock-code issues, device faults, service delays, customer-detail changes, field-agent access, suspected fraud and safety concerns. Before the underlying issue can be solved, someone still has to understand the message, judge urgency, route it and decide the next safe action.

## What I built

The reviewer demo uses **13 fixed support situations**. A reviewer selects a situation and sees the related **market, channel and customer/agent message as read-only case details**. The copilot then produces:

- Short summary
- Issue category
- Priority
- Owner team
- Recommended next action
- Draft response
- Confidence score
- Human-review flag

The **pilot dashboard changes with the selected situation**. Each case type shows its own synthetic case volume, AI-assist level, human-review requirement, route, case-specific metrics and control/guardrail.

The repository also includes:
- Batch CSV triage
- Overall synthetic operating dataset
- SQL analysis queries
- Automated tests
- Product brief, PRD, rollout plan and decision log
- Optional LLM API mode + no-key demo mode

## Why this is AI-first

I started with the repeated interpretation problem instead of a long feature specification. The prototype tests whether AI can reduce first-pass support work while keeping payment, identity, safety and risk decisions grounded in verified systems and human review.

The product uses AI for ambiguity: understanding language, summarizing, classifying and suggesting a route. It does **not** use generated text as the source of truth for money movement, identity or safety-sensitive actions.

## How a case is handled

1. **The case comes in.** The original message, market and channel stay attached to the case.
2. **A support user reviews the first pass.** The copilot summarizes the issue, suggests urgency and proposes the owning team. The user can accept or correct it.
3. **The owning team resolves the issue.** Payment, identity, safety and risk actions still depend on verified systems and people.
4. **The outcome is recorded.** Final route, override and resolution data are captured so the workflow can be measured and improved.

## Try it locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

The default **Demo mode** works without an API key.

### Optional real LLM mode

```text
LLM_API_KEY=...
LLM_MODEL=...
LLM_API_URL=https://api.openai.com/v1/chat/completions
```

The adapter expects an OpenAI-compatible chat-completions response. In production I would use a provider abstraction and structured-output validation rather than tightly coupling the workflow to one model.

## Safety boundaries

The copilot can summarize, classify, route and draft. It cannot automatically:
- Confirm a payment without checking the source system.
- Issue refunds or credits.
- Change customer identity/profile data.
- Close suspected fraud or safety cases.
- Decide warranty/replacement without verified service history.

## Pilot metrics

The demo changes metrics by situation because different workflows need different success measures. Examples include:

**Payments:** payment match rate, time to ledger check, unlock recovery, repeat contacts.  
**Service:** troubleshooting completion, technician response, repeat-failure rate, resolution time.  
**Risk/safety:** time to human escalation, investigation/inspection time, missed-escalation rate.  
**Identity:** identity-check completion and audit completeness.  
**Agent tools:** login recovery time, OTP failure rate and agent downtime.

Across the whole pilot I would still track AI usage, correct routing, human overrides, resolution time, backlog and repeat-contact rate.

## Repository structure

```text
app.py                         Streamlit prototype with fixed reviewer scenarios
src/triage.py                  demo + LLM triage logic and guardrails
src/analytics.py               overall dashboard metric calculations
data/synthetic_tickets.csv     synthetic operating dataset
data/batch_input_example.csv   sample batch upload
sql/product_usage_queries.sql  SQL for adoption/quality/ops metrics
tests/test_triage.py           automated routing/safety tests
docs/index.html                scenario-based GitHub Pages demo
docs/PRODUCT_BRIEF.md          problem, users, scope, metrics, risks
docs/PRD.md                    requirements and acceptance criteria
docs/TEST_AND_ROLLOUT_PLAN.md  pilot and launch approach
docs/AI_EXPERIENCE_SUMMARY.md  candidate AI background + evidence
docs/DECISION_LOG.md           product tradeoffs and reasoning
```

## What I would validate with real stakeholders

1. Actual top support intents and language mix by market.
2. Current routing rules, SLAs and escalation ownership.
3. Which APIs/source systems can verify payment, code and account state.
4. PII handling and retention requirements.
5. Connectivity constraints for field teams.
6. Baseline handling time before claiming any efficiency improvement.

## Public context used

- Sun King payment options / EasyBuy: https://sunking.com/payment-options/
- Sun King company site: https://sunking.com/
- Sun King careers / operating context: https://sunking.com/work-with-us/

## Key takeaway

The prototype is intentionally small. The product idea is not “use AI everywhere”; it is to reduce repeated interpretation work, show users a useful first pass, keep sensitive actions grounded in verified systems and people, and measure whether the workflow actually improves operations.
