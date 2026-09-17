# Test & Rollout Plan

## 1. Prototype tests

### Functional
- Correct field structure is returned.
- Payment/unlock issues trigger verification language.
- Fraud and identity-change messages require human review.
- Batch CSV returns one output row per input row.
- Missing LLM credentials do not break the reviewer demo.

### Data-quality
- No real customer data in repository.
- Synthetic rows are clearly marked.
- PII in free text is masked before sending to the LLM adapter where practical.

### Product-quality test set
Before production, create a manually labelled set of at least 200–500 historical, de-identified tickets per pilot market. Measure:
- Category accuracy
- Priority agreement
- Routing accuracy
- Unsafe-response rate
- Human override rate

## 2. Pilot design

### Phase 0 — baseline
Measure current handling time and routing quality for 2 weeks.

### Phase 1 — shadow mode
AI runs silently on real de-identified messages. Compare AI output with agent decisions. No customer impact.

### Phase 2 — copilot pilot
Expose suggestions to a small group of trained users. Agent must approve/edit before routing or sending.

### Phase 3 — limited automation
Only automate low-risk repetitive actions if evidence shows stable accuracy. Payment, identity, refunds and fraud remain human-controlled.

## 3. Launch gates
Example gates to agree with operations and risk stakeholders:
- High routing accuracy on labelled pilot data
- No critical safety/payment hallucinations in release test set
- Override rate stable or improving week-over-week
- Support users trained on escalation boundaries
- Monitoring dashboard and rollback path ready

## 4. Rollback
If severe errors or operational disruption appear:
1. Disable LLM mode.
2. Keep existing ticket workflow active.
3. Preserve logs for root-cause review.
4. Correct prompts/rules/integration before re-enabling.
