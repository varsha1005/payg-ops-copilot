# AI Experience Summary — Varsha Panguluri

My approach to AI is to use it as a practical product and workflow tool, not only as a model-building exercise.

## Foundations

- **Microsoft AI Product Manager certification — in progress.** I am building product-level understanding of how AI capabilities translate into user problems, product requirements, validation and responsible deployment.
- **Google Developers AI & ML certification.** My prior learning covered TensorFlow, model development, data preprocessing, neural networks and responsible AI.
- **Hands-on ML/XAI project work.** I have worked on cardiac image segmentation using 3D U-Net / attention and on solar-radiation prediction using machine-learning models. I used explainability methods including SHAP, Grad-CAM and LIME to make model output easier to interpret.

## AI-first product evidence: PAYG Ops Copilot

For this case study I started with a workflow question: **what repeated interpretation work could AI remove before a support issue reaches the right human?**

Instead of writing a long specification first, I built a working prototype that:
- Accepts unstructured support/field messages.
- Uses an LLM-ready triage layer to produce a summary, category, priority, route, next action and response draft.
- Adds explicit human-in-the-loop boundaries for payment, fraud and identity-sensitive cases.
- Supports batch processing for repetitive queues.
- Tracks adoption, overrides and resolution metrics so the product can be improved from usage data.
- Includes SQL queries, test cases, rollout gates and a safe fallback mode.

The main lesson from the prototype is that AI-first does not mean “automate everything.” The highest-value design is often to let AI handle ambiguity and repeated interpretation while deterministic rules, verified systems and humans control sensitive decisions.

## How I would continue learning

My next step would be to benchmark the same workflow across multiple LLM providers/models, build a labelled evaluation set, measure accuracy/cost/latency tradeoffs, and add retrieval from verified internal systems so generated responses are grounded in source data.
