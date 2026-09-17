# Product Brief — PAYG Ops Copilot

**Candidate:** Varsha Panguluri  
**Project type:** Independent case-study prototype using synthetic data  
**Target role:** Associate Product Manager — Digitization & Automation

## 1. Problem I chose

Sun King combines PAYG financing, field operations, customer service and technology. Public product information shows that EasyBuy customers make recurring payments through mobile money or cash and use payment-linked codes to keep products active. Support and field teams can therefore face repeated situations involving payments, access codes, device faults, service delays, profile changes, agent access, fraud and safety concerns.

Before anybody can solve the case, someone must read the message, understand the intent, decide urgency, route it and often prepare a response. That first step is repetitive but also risky: payment, identity, fraud and safety cases should not be automated blindly.

**Hypothesis:** an AI triage layer can reduce first-pass work while keeping people in control of sensitive actions.

## 2. Users

Primary users:
- Customer support / customer operations agents
- Field operations coordinators
- Internal tools support
- Payment operations teams

Secondary users:
- Product managers tracking adoption and workflow quality
- Operations leaders tracking backlog and resolution trends

## 3. Product goal

Help a support user move from an unstructured case to a safe first decision quickly: understand the issue, judge urgency, identify the right team and suggest the next action without replacing verified systems or human judgment.

The prototype is a copilot for the first part of support work, not an autonomous customer-service agent.

## 4. Reviewer demo design

The live demo uses **13 fixed sample situations** so every reviewer sees the same case context and can compare outputs consistently.

For each selected situation, the demo displays the **market, channel and message as fixed case details** rather than editable fields. The reviewer then runs triage on that case.

The **pilot dashboard changes with the selected situation**. It shows illustrative synthetic values for:
- Case volume in the pilot slice
- AI-assist usage
- Human-review requirement
- Primary route
- Case-specific success metrics
- The main control/guardrail for that workflow

This is a prototype choice for clarity and repeatability. A production version would receive live messages from the real support/ticket workflow.

## 5. MVP scope

### In scope
- Scenario-based reviewer demo
- Fixed case details: market, channel and message
- Category and priority prediction
- Routing recommendation
- Recommended next action
- Short response draft
- Human-review flag
- Scenario-specific pilot dashboard
- Batch CSV triage
- SQL queries for adoption and quality metrics
- Transparent demo mode plus optional LLM API mode

### Out of scope
- Real Sun King customer data
- Direct connection to payment ledgers or CRM
- Automatic refunds, credits or payment confirmation
- Automatic customer-profile changes
- Production authentication and role-based access
- Multi-language quality benchmarking

## 6. Why AI instead of only rules?

Rules work well when inputs are consistent. Field/customer messages are not: they can be short, incomplete, conversational and may combine more than one issue. An LLM can normalize this ambiguity into structured fields and a useful summary.

Deterministic controls are still useful for safety. The production design I would use is hybrid:

1. AI proposes the first-pass interpretation and route.
2. Hard controls force human review for sensitive workflows.
3. Source systems verify factual account/payment/service information.
4. A support or operations user approves/edits when required.
5. The final decision and outcome are logged for measurement.

## 7. Key product decisions

| Decision | Why | Tradeoff |
|---|---|---|
| Start with triage, not full automation | Lower risk and easier to measure value | Some manual work remains |
| Fixed reviewer scenarios | Makes the demo repeatable and prevents inconsistent manual inputs | Less open-ended than production intake |
| Scenario-specific dashboard | Different workflows need different success measures and controls | Metrics are illustrative, not validated business results |
| Human review for sensitive actions | Payment, identity, fraud and safety errors can have real consequences | Limits straight-through automation |
| No API key required for reviewer demo | Recruiter can test the prototype immediately | Demo mode is deterministic rather than a live LLM |
| Track overrides | Frequent corrections are a strong signal of quality/trust problems | Requires event instrumentation |

## 8. Success metrics

I would establish a baseline first, then compare pilot performance.

**Common pilot metrics**
- Time to routed ticket
- Time to first useful response
- Correct-routing rate
- Human override rate
- Resolution time
- Repeat-contact / reopen rate
- Adoption by market and channel

**Case-specific examples**
- Payment: payment match rate, time to ledger check, unlock-code recovery
- Safety/risk: time to human escalation, investigation/inspection time
- Service: technician response, repeat-failure rate, repair vs replacement outcome
- Identity: identity-check completion, audit completeness
- Agent tools: login recovery time, OTP failure rate, agent downtime

## 9. Rollout approach

1. **Baseline:** measure current handling time, routing quality and repeat contacts.
2. **Shadow mode:** run on de-identified real messages and compare with human decisions.
3. **Copilot pilot:** expose suggestions to a small trained support group in one market/channel.
4. **Measure:** review route accuracy, overrides, time saved, safety errors and user feedback by case type.
5. **Improve:** refine categories, prompts, controls and source-system retrieval.
6. **Expand:** add more workflows only after agreed quality thresholds are met.

## 10. Main risks and controls

| Risk | Control |
|---|---|
| Hallucinated payment status | Never let generated text confirm payment; verify against ledger/API |
| Wrong routing | Easy human correction + labelled audit sample |
| PII leakage | Minimize/mask PII and define retention with privacy/security stakeholders |
| Fraud/safety missed | Hard escalation rules plus human review |
| Language performance varies | Market-specific labelled test sets before rollout |
| Agents stop trusting tool | Keep output concise and capture override feedback |

## 11. Key takeaway

The AI value is not “a chatbot.” It is reducing repeated interpretation and coordination work around a real operational workflow while keeping the support team in control and making quality measurable.
