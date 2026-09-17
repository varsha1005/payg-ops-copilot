# Decision Log

This file records the main product choices so the project shows reasoning, not only code.

| Date | Decision | Reason | Tradeoff |
|---|---|---|---|
| Prototype | Focus on support triage rather than a generic chatbot | Closely matches Digitization & Automation responsibilities and has measurable workflow value | Less visually flashy than a consumer chatbot |
| Prototype | Synthetic data only | No access to Sun King internal data; avoids false claims | Cannot prove real business impact yet |
| Prototype | Human-in-the-loop for sensitive actions | Payment, fraud and identity errors can have real consequences | Some manual work remains |
| Prototype | Reviewer-friendly demo mode | Recruiter can test without secrets/API cost | Demo mode is rules-based, not a true LLM |
| Prototype | Optional LLM adapter | Shows how the same workflow becomes AI-powered | Requires configured provider credentials |
| Prototype | Track human overrides | Overrides are a strong signal of product/model quality | Requires event instrumentation |
