from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.triage import triage_message

SCENARIOS = {
    "Payment not reflected + no unlock code": {"market":"Kenya","channel":"WhatsApp","message":"Customer says: I paid by mobile money this morning but the payment is not showing and I did not receive the unlock code.","case_count":13,"ai_assist":82,"review":"Required","route":"Payments / Customer Operations","focus":["Payment match rate","Time to ledger check","Unlock-code recovery","Repeat-contact rate"],"control":"Do not confirm a payment or resend access until the transaction is verified in the source system."},
    "Unlock code received but invalid": {"market":"Uganda","channel":"Call notes","message":"Customer says the payment went through and an unlock code was received, but the code is showing invalid on the keypad and the system is still locked.","case_count":6,"ai_assist":80,"review":"Required","route":"Payments / Customer Operations","focus":["Code verification time","Valid-code resend rate","Escalation rate","Repeat-contact rate"],"control":"Verify the latest successful payment and code state before sending or regenerating a code."},
    "Solar system stopped charging": {"market":"Tanzania","channel":"WhatsApp","message":"Customer says the solar system stopped charging yesterday. The panel is in sunlight but the battery level stays at zero and there is no power at night.","case_count":9,"ai_assist":76,"review":"Agent approval","route":"Service Operations","focus":["Troubleshooting completion","Technician visit rate","Resolution time","First-contact resolution"],"control":"The support user reviews the troubleshooting suggestion before a field-service visit is created."},
    "Battery smoke / safety concern": {"market":"Kenya","channel":"Call notes","message":"Customer reports that the battery became very hot and started producing smoke. They switched the system off and are worried it may catch fire.","case_count":2,"ai_assist":35,"review":"Required - urgent","route":"Safety / Service Operations","focus":["Time to human escalation","Safety acknowledgement time","Field response time","Closure after inspection"],"control":"Safety cases stop normal automation and are escalated immediately to a person."},
    "Technician did not arrive": {"market":"Nigeria","channel":"Ticketing tool","message":"Customer says installation was booked for yesterday, but the technician did not arrive and nobody called to reschedule. The customer has already paid the deposit.","case_count":7,"ai_assist":86,"review":"Agent approval","route":"Field Service Operations","focus":["Overdue appointments","Reschedule time","Technician response","Customer follow-up"],"control":"The tool can suggest the next step, but actual scheduling comes from the field-service system."},
    "Customer wants phone number changed": {"market":"Kenya","channel":"Email","message":"Customer says the phone number linked to the account is no longer active and asks support to replace it with a new number so payment messages go to the correct phone.","case_count":5,"ai_assist":45,"review":"Required","route":"Customer Operations","focus":["Identity-check completion","Profile-change turnaround","Rejected change requests","Audit completeness"],"control":"Customer identity must be verified through the approved process before profile details are changed."},
    "Customer asks for remaining balance": {"market":"Uganda","channel":"WhatsApp","message":"Customer asks how much balance is left on the payment plan, what the next installment amount is, and when the next payment is due.","case_count":8,"ai_assist":92,"review":"Not normally required","route":"Customer Support","focus":["Verified balance retrieval","Response time","Self-service completion","Repeat-contact rate"],"control":"Any balance or due-date answer must come from verified account data, not generated text."},
    "Cash paid to agent but not recorded": {"market":"Nigeria","channel":"Agent app","message":"Customer says they gave cash to a field agent two days ago and received a handwritten receipt, but the payment is still missing from the account and the product remains locked.","case_count":4,"ai_assist":40,"review":"Required","route":"Risk / Operations","focus":["Cash reconciliation time","Receipt verification","Agent investigation time","Customer resolution time"],"control":"Preserve evidence and route to human investigation before any payment or account action."},
    "Customer suspects a fake agent / scam": {"market":"Kenya","channel":"WhatsApp","message":"Customer says a person claiming to be a Sun King agent asked them to send money to a personal mobile number. The customer suspects it may be a scam and wants the agent verified.","case_count":2,"ai_assist":25,"review":"Required - urgent","route":"Risk / Operations","focus":["Time to escalation","Agent verification time","Potential-loss prevention","Case closure time"],"control":"Tell the customer not to send more money and move the case immediately to human risk review."},
    "Battery failed again; warranty request": {"market":"Uganda","channel":"Ticketing tool","message":"Customer says the battery was repaired last month but it has stopped working again. They want to know whether it is still under warranty and whether a replacement can be arranged.","case_count":5,"ai_assist":65,"review":"Required","route":"Service Operations","focus":["Warranty eligibility time","Repeat-repair rate","Replacement approval time","Resolution time"],"control":"Warranty and replacement decisions use verified service history and policy rules, not the generated recommendation alone."},
    "Delivery missing a component": {"market":"Tanzania","channel":"Email","message":"Customer received the solar kit today, but the package is missing the charging cable and one light. They want the missing items delivered.","case_count":6,"ai_assist":88,"review":"Agent approval","route":"Logistics / Customer Operations","focus":["Order verification time","Missing-item rate","Fulfillment turnaround","Customer follow-up"],"control":"Confirm the order and delivery record before creating a replacement fulfillment request."},
    "Field agent cannot log in to app": {"market":"Myanmar","channel":"Agent app","message":"Field agent says they cannot log in to the agent app after changing phones. OTP verification keeps failing and they cannot register today's customer payments.","case_count":8,"ai_assist":84,"review":"Agent approval","route":"Internal Tools Support","focus":["Login recovery time","OTP failure rate","Agent downtime","Escalation rate"],"control":"Account recovery follows approved authentication steps; the copilot cannot bypass access controls."},
    "Product failed repeatedly after service": {"market":"Nigeria","channel":"Call notes","message":"Customer says the solar unit has failed for the third time even after two technician visits. They are frustrated and want the issue permanently resolved.","case_count":5,"ai_assist":50,"review":"Required","route":"Service Operations","focus":["Repeat-failure rate","Prior-visit review","Repair vs replacement decision","Final resolution time"],"control":"A human reviews service history before deciding whether another repair or a replacement path is appropriate."},
}

st.set_page_config(page_title="PAYG Ops Copilot", page_icon="☀️", layout="wide")
st.title("PAYG Ops Copilot")
st.caption("AI-first support triage + operations analytics prototype | Synthetic data only")

with st.sidebar:
    st.header("Prototype settings")
    available_llm = bool(os.getenv("LLM_API_KEY") and os.getenv("LLM_MODEL"))
    mode_label = st.radio("Triage engine", ["Demo mode (no key needed)", "LLM API mode"], index=0, help="Demo mode uses transparent deterministic rules so a reviewer can test the workflow without credentials.")
    mode = "llm" if mode_label.startswith("LLM") else "demo"
    if mode == "llm" and not available_llm:
        st.warning("LLM mode needs LLM_API_KEY and LLM_MODEL. This run will fall back to demo mode if they are missing.")
    st.markdown("---")
    st.markdown("**Safety rule:** the copilot recommends and drafts, but verified systems and people remain responsible for sensitive actions.")

if "selected_scenario" not in st.session_state:
    st.session_state["selected_scenario"] = next(iter(SCENARIOS))

triage_tab, dashboard_tab, batch_tab, design_tab = st.tabs(["1. Review a case", "2. Pilot dashboard", "3. Batch automation", "4. Product design"])

with triage_tab:
    st.subheader("Review a realistic support situation")
    scenario_name = st.selectbox("Situation", list(SCENARIOS.keys()), index=list(SCENARIOS.keys()).index(st.session_state["selected_scenario"]))
    st.session_state["selected_scenario"] = scenario_name
    case = SCENARIOS[scenario_name]

    c1, c2 = st.columns(2)
    c1.markdown(f"**Market**  \n{case['market']}")
    c2.markdown(f"**Channel**  \n{case['channel']}")
    st.markdown("**Message**")
    st.info(case["message"])

    if st.button("Triage case", type="primary"):
        selected_mode = mode
        if selected_mode == "llm" and not available_llm:
            selected_mode = "demo"
            st.info("LLM credentials are not configured, so this run used demo mode.")
        try:
            result = triage_message(case["message"], market=case["market"], channel=case["channel"], mode=selected_mode)
        except Exception as exc:
            st.error(f"LLM call failed: {exc}")
            st.info("Falling back to demo mode for this case.")
            result = triage_message(case["message"], market=case["market"], channel=case["channel"], mode="demo")
        st.session_state["last_result"] = result.to_dict()
        st.session_state["last_result_scenario"] = scenario_name

    if st.session_state.get("last_result_scenario") == scenario_name and "last_result" in st.session_state:
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
            st.warning("Human review required before any sensitive, payment-dependent, identity-changing, or risk action.")

with dashboard_tab:
    scenario_name = st.session_state["selected_scenario"]
    case = SCENARIOS[scenario_name]
    st.subheader("Pilot dashboard for the selected situation")
    st.caption("Illustrative synthetic metrics. They demonstrate how a pilot view could change by case type; they are not Sun King performance data.")
    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Synthetic cases", case["case_count"])
    d2.metric("AI assist usage", f"{case['ai_assist']}%")
    d3.metric("Human review", case["review"])
    d4.metric("Primary route", case["route"])
    left, right = st.columns([1.2, 0.8])
    with left:
        st.markdown("**What I would watch for this case type**")
        for metric in case["focus"]:
            st.write(f"• {metric}")
    with right:
        st.markdown("**Case control**")
        st.info(case["control"])
    df = pd.read_csv(ROOT / "data" / "synthetic_tickets.csv")
    st.markdown("**Overall synthetic pilot context**")
    overall1, overall2, overall3 = st.columns(3)
    overall1.metric("All synthetic tickets", len(df))
    overall2.metric("Markets represented", df["market"].nunique())
    overall3.metric("Channels represented", df["channel"].nunique())

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
            st.download_button("Download triaged CSV", data=output.to_csv(index=False).encode("utf-8"), file_name="triaged_tickets.csv", mime="text/csv")

with design_tab:
    st.subheader("How a support team would handle a case")
    st.markdown("""
1. **The case comes in.** The original message, market and channel stay attached to the case.
2. **A support user reviews the first pass.** The copilot summarizes the issue, suggests urgency and proposes the owning team. The user can accept or correct it.
3. **The owning team resolves the issue.** Payment, identity, safety and risk actions still depend on verified systems and human approval.
4. **The outcome is recorded.** The team captures the final route, whether the suggestion was overridden, and the resolution result so the product can be improved.

**What I would measure**
- Time to routed ticket and first useful response
- Correct routing and human override rate
- Resolution time and repeat-contact rate
- Adoption by market/channel
- Safety or risk escalation misses

**What I would validate before rollout**
- Top real support intents and language mix by market
- Existing ownership rules and escalation SLAs
- APIs that can safely verify payment/account state
- PII and audit-log requirements
- Field connectivity and mobile-workflow constraints
""")
