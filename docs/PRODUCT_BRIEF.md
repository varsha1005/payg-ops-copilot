# Product Brief — PAYG Ops Copilot

**Candidate:** Varsha Panguluri  
**Project type:** Independent case-study prototype using synthetic data  
**Target role:** Associate Product Manager — Digitization & Automation

## 1. Problem I chose

Sun King combines PAYG financing, field operations, customer service and technology. Public product information shows that EasyBuy customers make recurring payments through mobile money or cash and use payment-linked codes to keep products active. At this scale, support teams can receive repeated questions such as:

- “I paid, but the payment is not showing.”
- “I did not receive my unlock code.”
- “The installer has not arrived.”
- “My agent app login is failing.”
- “How much balance is left?”

The raw messages can come from WhatsApp, email, call notes, ticketing tools or field teams. Before anybody can solve the case, someone must read the message, understand the intent, decide urgency, route it, and often draft a response. That first step is repetitive but also risky: payment, identity and fraud cases should not be automated blindly.

**Hypothesis:** an AI triage layer can reduce the manual first-pass work while keeping humans in control of sensitive actions.

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

Convert an unstructured incoming support message into a structured, action-ready ticket in seconds:

`message → summary → category → priority → owner → next action → response draft → guardrail → event log`

The prototype does **not** try to become an autonomous customer-service agent. It is a copilot for the first 30–90 seconds of support work.

## 4. MVP scope

### In scope
- Single-message triage
- Category and priority prediction
- Routing recommendation
- Recommended next action
- Short response draft
- Human-review flag
- Batch CSV triage
- Usage/operations dashboard
- SQL queries for adoption and quality metrics
- Transparent demo mode plus optional LLM API mode

### Out of scope
- Real Sun King customer data
- Direct connection to payment ledgers or CRM
- Automatic refunds, credits or payment confirmation
- Automatic customer-profile changes
- Production authentication and role-based access
- Multi-language quality benchmarking

## 5. Why AI instead of only rules?

Rules work well when inputs are consistent. Field/customer messages are not: they are short, incomplete, conversational, sometimes multilingual and often combine more than one issue. An LLM can normalize this ambiguity into structured fields and a useful summary.

However, deterministic rules are still useful as guardrails. My proposed production design is hybrid:

1. LLM understands and structures the message.
2. Hard rules block unsafe actions and force review for specific intents.
3. Source systems verify factual account/payment information.
4. Human agents handle sensitive or low-confidence cases.

## 6. Key product decisions

| Decision | Why |
|---|---|
| Start with triage, not full automation | Lower risk and easier to measure value |
| Keep a human-review flag | Payment, identity, fraud and low-confidence cases need judgment |
| No API key required for reviewer demo | Recruiter can test the prototype immediately |
| Synthetic data only | Avoid pretending to have internal data |
| Track overrides | If humans keep changing AI output, the model/workflow needs improvement |
| Track adoption by market/channel | Rollouts should be sequenced based on actual usage and workflow fit |

## 7. Success metrics

I would establish a 2–4 week baseline first, then compare pilot performance.

**Efficiency**
- Median time from incoming message to routed ticket
- Median time to first useful response
- Backlog older than 24 hours

**Quality**
- Correct-routing rate from human audit sample
- Human override rate
- Reopen / repeat-contact rate
- Safety escalation miss rate

**Adoption**
- % of eligible tickets triaged with AI
- Weekly active support users
- Adoption by market and channel

**Business / user outcome**
- Resolution time by issue type
- Agent satisfaction with the copilot
- Customer repeat-contact rate

## 8. Rollout approach

1. **Shadow mode:** AI generates output but agents do not see it. Compare against human labels.
2. **Copilot pilot:** show suggestions to a small support group in one market/channel.
3. **Measure:** routing accuracy, override rate, time saved, safety errors.
4. **Improve:** refine prompt, categories and source-system retrieval.
5. **Expand:** add more markets/channels only after quality thresholds are met.

## 9. Main risks and controls

| Risk | Control |
|---|---|
| Hallucinated payment status | Never let the LLM confirm payment; verify against ledger/API |
| Wrong routing | Confidence threshold + easy human override + weekly audit |
| PII leakage | Mask PII in model input where possible; minimal retention |
| Fraud/safety missed | Keyword/rule guardrail plus human escalation |
| Language performance varies | Market-specific test sets before rollout |
| Agents stop trusting tool | Show concise reasoning; capture override feedback |

## 10. Key takeaway

The AI value is not “a chatbot.” It is removing repeated interpretation and coordination work around a high-volume workflow, while making the product measurable through adoption and quality data.
