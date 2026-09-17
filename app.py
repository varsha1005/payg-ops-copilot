from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.analytics import dashboard_metrics
from src.triage import triage_message

st.set_page_config(page_title="PAYG Ops Copilot", page_icon="☀️", layout="wide")

st.title("PAYG Ops Copilot")
st.caption("AI-first support triage + operations analytics prototype | Synthetic data only")

with st.sidebar:
    st.header("Prototype settings")
    available_llm = bool(os.getenv("LLM_API_KEY") and os.getenv("LLM_MODEL"))
    mode_label = st.radio(
        "Triage engine",
        ["Demo mode (no key needed)", "LLM API mode"],
        index=0,
        help="Demo mode uses transparent deterministic rules so anyone reviewing the project can test it. LLM mode uses an OpenAI-compatible API endpoint configured through environment variables.",
    )
    mode = "llm" if mode_label.startswith("LLM") else "demo"
    if mode == "llm" and not available_llm:
        st.warning("LLM mode needs LLM_API_KEY and LLM_MODEL environment variables. The app will fall back to demo mode if they are missing.")
    st.markdown("---")
    st.markdown("**Safety rule:** the copilot can recommend and draft, but it does not confirm payments, issue refunds, or change customer details without verification.")

triage_tab, dashboard_tab, batch_tab, design_tab = st.tabs(
    ["1. Triage a message", "2. Ops dashboard", "3. Batch automation", "4. Product design"]
)

with triage_tab:
    st.subheader("Turn an unstructured message into an action-ready ticket")
    c1, c2 = st.columns(2)
    market = c1.selectbox("Market", ["Kenya", "Uganda", "Nigeria", "Tanzania", "Myanmar", "Other"])
    channel = c2.selectbox("Channel", ["WhatsApp", "Ticketing tool", "Email", "Call notes", "Agent app"])

    default_message = "Customer says: I paid by mobile money this morning but the payment is not showing and I did not receive the unlock code. Transaction ref AB12345678."
    message = st.text_area("Incoming message", value=default_message, height=130)

    if st.button("Triage message", type="primary"):
        selected_mode = mode
        if selected_mode == "llm" and not available_llm:
            selected_mode = "demo"
            st.info("LLM credentials are not configured, so this run used demo mode.")
        try:
            result = triage_message(message, market=market, channel=channel, mode=selected_mode)
            st.session_state["last_result"] = result.to_dict()
        except Exception as exc:
            st.error(f"LLM call failed: {exc}")
            st.info("Falling back to demo mode for this message.")
            result = triage_message(message, market=market, channel=channel, mode="demo")
            st.session_state["last_result"] = result.to_dict()

    if "last_result" in st.session_state:
        r = st.session_state["last_result"]
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Category", r["category"])
        m2.metric("Priority", r["priority"])
        m3.metric("Confidence", f"{r['confidence']:.0%}")
        m4.metric("Human review", "Yes" if r["needs_human_review"] else "No")

        left, right = st.columns(2)
        with left:
            st.markdown("**Summary**")
            st.write(r["summary"])
            st.markdown("**Owner team**")
            st.write(r["owner_team"])
            st.markdown("**Why this priority**")
            st.write(r["reason"])
        with right:
            st.markdown("**Recommended next action**")
            st.write(r["recommended_action"])
            st.markdown("**Draft response**")
            st.info(r["response_draft"])

        if r["needs_human_review"]:
            st.warning("Human review required before any account-changing or payment-dependent action.")

with dashboard_tab:
    st.subheader("Usage and operations dashboard")
    df = pd.read_csv(ROOT / "data" / "synthetic_tickets.csv")
    metrics = dashboard_metrics(df)

    k1, k2, k3, k4, k5, k6 = st.columns(6)
    k1.metric("Tickets", metrics["tickets"])
    k2.metric("Open", metrics["open"])
    k3.metric("High/Urgent", metrics["high_or_urgent"])
    k4.metric("Avg resolution", f"{metrics['avg_resolution_hours']} h")
    k5.metric("AI usage", f"{metrics['ai_adoption_pct']}%")
    k6.metric("Human overrides", f"{metrics['human_override_pct']}%")

    st.caption("These numbers are generated from synthetic prototype data. In production, they would come from the ticketing and product-usage data warehouse.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Tickets by category**")
        st.bar_chart(df["category"].value_counts())
    with c2:
        st.markdown("**Tickets by market**")
        st.bar_chart(df["market"].value_counts())

    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**Average resolution time by category (hours)**")
        chart = (
            df[df["status"] == "Resolved"]
            .groupby("category")["resolution_hours"]
            .mean()
            .sort_values(ascending=False)
        )
        st.bar_chart(chart)
    with c4:
        st.markdown("**Human override rate by category**")
        override = (
            df[df["ai_used"] == 1]
            .groupby("category")["human_override"]
            .mean()
            .mul(100)
            .sort_values(ascending=False)
        )
        st.bar_chart(override)

    st.markdown("**Recent synthetic tickets**")
    st.dataframe(
        df[["ticket_id", "market", "channel", "category", "priority", "status", "resolution_hours", "ai_used", "human_override"]].head(20),
        use_container_width=True,
        hide_index=True,
    )

with batch_tab:
    st.subheader("Batch-triage a CSV")
    st.write("Upload a CSV with columns `message`, `market`, and `channel`. This simulates automating a backlog or daily support queue.")
    upload = st.file_uploader("Upload CSV", type=["csv"])
    if upload is not None:
        batch = pd.read_csv(upload)
        required = {"message", "market", "channel"}
        if not required.issubset(batch.columns):
            st.error(f"Missing required columns: {sorted(required - set(batch.columns))}")
        else:
            rows = []
            for _, row in batch.iterrows():
                selected_mode = "llm" if mode == "llm" and available_llm else "demo"
                try:
                    triage = triage_message(str(row["message"]), str(row["market"]), str(row["channel"]), selected_mode)
                except Exception:
                    triage = triage_message(str(row["message"]), str(row["market"]), str(row["channel"]), "demo")
                rows.append({**row.to_dict(), **triage.to_dict()})
            output = pd.DataFrame(rows)
            st.dataframe(output, use_container_width=True)
            st.download_button(
                "Download triaged CSV",
                data=output.to_csv(index=False).encode("utf-8"),
                file_name="triaged_tickets.csv",
                mime="text/csv",
            )

with design_tab:
    st.subheader("Why this is an AI-first product, not just a chatbot")
    st.markdown(
        """
**Workflow:** incoming WhatsApp/email/ticket message → AI extraction and classification → guardrail check → routing → human review when needed → action/response → event log → usage analytics.

**Human-in-the-loop boundaries**
- AI can summarize, classify, route, draft, and recommend.
- AI cannot confirm money movement without a verified ledger lookup.
- AI cannot issue refunds, credits, ownership changes, or sensitive profile changes.
- Low-confidence, fraud/safety, and identity-change cases go to a person.

**Product metrics I would track**
- Median time to first useful response.
- Correct routing rate and human override rate.
- % of tickets triaged with AI.
- Resolution time by issue category and market.
- Reopen rate and repeat-contact rate.
- Backlog older than 24 hours.

**What I would validate before rollout**
- Top real support intents and language mix by market.
- Current ticket ownership rules and escalation SLAs.
- Which source systems can safely verify payment and account status.
- PII retention requirements and audit-log requirements.
- Field-team connectivity constraints and mobile workflow needs.
"""
    )
