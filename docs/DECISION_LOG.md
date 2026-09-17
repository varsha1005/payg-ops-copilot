# Decision Log

This file records the main product choices so the project shows reasoning, not only code.

| Date | Decision | Reason | Tradeoff |
|---|---|---|---|
| Prototype | Focus on support triage rather than a generic chatbot | Closely matches Digitization & Automation responsibilities and has measurable workflow value | Less visually flashy than a consumer chatbot |
| Prototype | Synthetic data only | No access to Sun King internal data; avoids false claims | Cannot prove real business impact yet |
| Prototype | Human-in-the-loop for sensitive actions | Payment, fraud, safety, identity and policy-sensitive errors can have real consequences | Some manual work remains |
| Prototype | Use fixed reviewer scenarios | Makes the demo repeatable and lets reviewers compare different risk levels without inventing inputs | Less open-ended than a production intake form |
| Prototype | Show market/channel/message as read-only case context | Keeps attention on product decisions rather than form entry | Reviewer cannot edit the sample case |
| Prototype | Make pilot dashboard situation-specific | Each workflow needs different metrics and controls | Values are illustrative until a real pilot exists |
| Prototype | Reviewer-friendly demo mode | Recruiter can test without secrets/API cost | Demo mode is deterministic, not a live LLM |
| Prototype | Optional LLM adapter | Shows how the same workflow becomes AI-powered | Requires configured provider credentials |
| Prototype | Track human overrides | Overrides are a strong signal of product/model quality | Requires event instrumentation |
