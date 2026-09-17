# Test & Rollout Plan

## 1. Prototype tests

### Functional
- Selecting a scenario displays the correct fixed market, channel and message.
- Payment/unlock issues trigger verification language.
- Safety and fraud cases are urgent and require human review.
- Identity changes require verification before update.
- Delivery cases route to logistics/customer operations.
- Warranty and repeated-failure cases require service-history review.
- The pilot dashboard changes when the selected situation changes.
- Batch CSV returns one output row per input row.
- Missing LLM credentials do not break the reviewer demo.

### Automated checks
The packaged heuristic test suite currently covers nine core routing/safety behaviors and passes **9/9 tests** in the project environment.

### Data-quality
- No real customer data in repository.
- Synthetic/illustrative values are clearly labelled.
- PII in free text is masked before sending to the LLM adapter where practical.

### Product-quality test set
Before production, create a manually labelled set of at least 200–500 historical, de-identified tickets per pilot market. Measure:
- Category accuracy
- Priority agreement
- Routing accuracy
- Unsafe-response rate
- Human override rate
- Safety/risk escalation recall

## 2. Pilot design

### Phase 0 — baseline
Measure current handling time, routing quality and repeat contacts.

### Phase 1 — shadow mode
AI runs silently on real de-identified messages. Compare its first-pass interpretation and route with the human decision. No customer impact.

### Phase 2 — copilot pilot
Expose suggestions to a small trained support group. The user approves/edits before routing or sending.

### Phase 3 — workflow-specific automation
Only automate low-risk repetitive actions when evidence shows stable quality. Payment, identity, refunds, fraud, safety and policy-sensitive service decisions remain controlled by people/verified systems.

## 3. Dashboard validation
For each case type, confirm that the pilot view surfaces metrics relevant to that workflow. Examples:
- Payment: ledger-check time and payment match rate
- Safety/risk: time to human escalation
- Service: technician response and repeat-failure rate
- Identity: verification completion and audit trail
- Agent tools: login recovery time and downtime

## 4. Launch gates
Example gates to agree with operations and risk stakeholders:
- High routing accuracy on labelled pilot data
- No critical safety/payment hallucinations in the release test set
- Safety/risk cases consistently escalate to a person
- Override rate stable or improving week over week
- Support users trained on escalation boundaries
- Monitoring dashboard and rollback path ready

## 5. Rollback
If severe errors or operational disruption appear:
1. Disable LLM mode.
2. Keep the existing ticket workflow active.
3. Preserve logs for root-cause review.
4. Correct prompts, rules or integration before re-enabling.
