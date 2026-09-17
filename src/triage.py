from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, asdict
from typing import Any, Dict

import requests


@dataclass
class TriageResult:
    summary: str
    category: str
    priority: str
    owner_team: str
    recommended_action: str
    response_draft: str
    confidence: float
    needs_human_review: bool
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _contains_any(text: str, terms: list[str]) -> bool:
    return any(term in text for term in terms)


def _mask_pii(text: str) -> str:
    text = re.sub(r"\b\+?\d[\d\s-]{8,}\d\b", "[PHONE/ID MASKED]", text)
    text = re.sub(r"\b[A-Z0-9]{8,}\b", "[REFERENCE MASKED]", text)
    return text


def heuristic_triage(message: str, market: str = "Unknown", channel: str = "Unknown") -> TriageResult:
    raw = message.strip()
    text = raw.lower()

    category = "Other / needs review"
    priority = "Medium"
    owner = "Customer Operations"
    confidence = 0.58
    human = True
    reason = "Intent is not clear enough for safe automation."

    if _contains_any(text, ["smoke", "fire", "burning", "sparks", "very hot", "overheating"]):
        category = "Product safety issue"
        priority = "Urgent"
        owner = "Safety / Service Operations"
        confidence = 0.96
        human = True
        reason = "Possible product safety risk should bypass normal automation and reach a person immediately."
    elif _contains_any(text, ["fraud", "scam", "fake agent", "personal mobile number", "agent took", "cash missing", "stolen"]):
        category = "Payment / risk concern"
        priority = "Urgent"
        owner = "Risk / Operations"
        confidence = 0.94
        human = True
        reason = "Potential fraud or cash-handling risk requires human investigation before any account action."
    elif _contains_any(text, ["warranty", "replacement", "replace"]) and _contains_any(text, ["battery", "device", "system", "repair", "working", "stopped"]):
        category = "Warranty / replacement request"
        priority = "Medium"
        owner = "Service Operations"
        confidence = 0.88
        human = True
        reason = "Warranty and replacement decisions depend on verified service history and policy eligibility."
    elif _contains_any(text, ["third time", "again", "repeated", "two technician", "two visits"]) and _contains_any(text, ["battery", "solar", "device", "system", "unit", "failed", "working"]):
        category = "Repeat product failure"
        priority = "High"
        owner = "Service Operations"
        confidence = 0.89
        human = True
        reason = "Repeated failure needs prior-service review and a human decision on the next corrective path."
    elif _contains_any(text, ["delivery", "package", "kit", "received"]) and _contains_any(text, ["missing", "not included", "did not receive"]):
        category = "Delivery / missing component"
        priority = "Medium"
        owner = "Logistics / Customer Operations"
        confidence = 0.88
        human = False
        reason = "Order and delivery records should be checked before a missing-item fulfillment request is created."
    elif _contains_any(text, ["paid", "payment", "mpesa", "m-pesa", "mobile money", "cash", "deposit", "transaction", "receipt"]) and _contains_any(text, ["not reflect", "not showing", "missing", "still locked", "not updated", "not credited", "did not receive", "no unlock"]):
        category = "Payment not reflected"
        priority = "High"
        owner = "Payments / Customer Operations"
        confidence = 0.90
        human = True
        reason = "Payment/access status must be checked in a source system before any payment-dependent response or action."
    elif _contains_any(text, ["unlock", "code", "token", "keypad"]) and _contains_any(text, ["not received", "not working", "invalid", "wrong", "failed", "no code", "still locked"]):
        category = "Unlock code issue"
        priority = "High"
        owner = "Payments / Customer Operations"
        confidence = 0.88
        human = True
        reason = "Code handling depends on verified payment and code state."
    elif _contains_any(text, ["install", "technician", "service", "visit", "appointment"]) and _contains_any(text, ["delay", "waiting", "did not arrive", "did not come", "not come", "late", "reschedule", "pending"]):
        category = "Installation / service delay"
        priority = "Medium"
        owner = "Field Service Operations"
        confidence = 0.86
        human = False
        reason = "The case needs scheduling/status verification and field-team follow-up."
    elif _contains_any(text, ["agent", "app", "login", "password", "otp", "account", "sync"]) and _contains_any(text, ["cannot", "can't", "cant", "failed", "locked", "error", "not syncing", "unable", "keeps failing"]):
        category = "Agent app / access issue"
        priority = "Medium"
        owner = "Internal Tools Support"
        confidence = 0.88
        human = False
        reason = "This is an internal productivity/access issue and should follow approved recovery steps."
    elif _contains_any(text, ["phone", "number", "name", "details", "contact"]) and _contains_any(text, ["change", "update", "wrong", "new number", "replace"]):
        category = "Customer details update"
        priority = "Medium"
        owner = "Customer Operations"
        confidence = 0.88
        human = True
        reason = "Customer identity must be verified before profile information is changed."
    elif _contains_any(text, ["balance", "remaining", "installment", "instalment", "payment plan", "due", "payoff"]):
        category = "Payment plan / balance query"
        priority = "Low"
        owner = "Customer Support"
        confidence = 0.87
        human = False
        reason = "This is a routine account query, but the values must come from verified account data."
    elif _contains_any(text, ["solar", "battery", "lamp", "light", "panel", "fan", "tv", "device", "system", "unit"]) and _contains_any(text, ["not working", "dead", "off", "won't turn", "wont turn", "fault", "broken", "stopped", "no power", "not charging", "zero"]):
        category = "Device / product issue"
        priority = "Medium"
        owner = "Service Operations"
        confidence = 0.86
        human = False
        reason = "The case can start with standard troubleshooting and service-status checks."

    safe_text = _mask_pii(raw)
    summary = safe_text[:180] + ("..." if len(safe_text) > 180 else "")

    action_map = {
        "Product safety issue": "Ask the customer to stop using the product, then escalate immediately to the safety/service team for verified next steps.",
        "Payment / risk concern": "Preserve the case details and evidence, prevent further risky action, verify the agent/account, and escalate for human investigation.",
        "Warranty / replacement request": "Review warranty eligibility and prior repair history before any replacement or service commitment is made.",
        "Repeat product failure": "Review prior service history and assign a human owner to decide whether repair, replacement, or deeper diagnosis is appropriate.",
        "Delivery / missing component": "Confirm the order contents and delivery record, then create a fulfillment request for any verified missing component.",
        "Payment not reflected": "Check the transaction reference and payment ledger; confirm whether payment posted; resend or regenerate access only after verification.",
        "Unlock code issue": "Verify the latest successful payment and code status; resend a valid code or escalate if code generation failed.",
        "Installation / service delay": "Check appointment status, propose the next available slot, and alert the field coordinator if the case is overdue.",
        "Agent app / access issue": "Validate agent account status, follow approved OTP/password recovery, and escalate persistent authentication or sync errors.",
        "Customer details update": "Verify customer identity using the approved process before changing contact or account details.",
        "Payment plan / balance query": "Retrieve verified balance and plan details, then explain the next amount/date in simple language.",
        "Device / product issue": "Run the standard troubleshooting checklist, verify service/warranty status, and create a technician visit if unresolved.",
        "Other / needs review": "Ask one clarifying question, then route to the relevant operations owner. Do not take account-changing action automatically.",
    }

    response_map = {
        "Product safety issue": "Thank you for reporting this. Please keep the system switched off and stop using it. I am escalating this as a safety case so the service team can contact you with the next safe step.",
        "Payment / risk concern": "Thank you for flagging this. Please do not send any additional money until the details are verified. I have escalated the case for human review.",
        "Warranty / replacement request": "Thanks for the details. We will review the previous repair and warranty status before confirming the next service or replacement step.",
        "Repeat product failure": "I can see this is a repeat issue. The team will review the previous service history before deciding the next corrective action.",
        "Delivery / missing component": "Thanks for reporting the missing item. We will check the order and delivery record, then arrange the next fulfillment step for any confirmed missing component.",
    }
    response_draft = response_map.get(category, "Thanks for reporting this. I have captured the issue and routed it to the right team. We will verify the relevant account, payment, or service details before making any sensitive changes.")

    return TriageResult(summary=summary, category=category, priority=priority, owner_team=owner, recommended_action=action_map[category], response_draft=response_draft, confidence=round(confidence, 2), needs_human_review=human or confidence < 0.75, reason=reason)


SYSTEM_PROMPT = """You are an operations triage assistant for a PAYG solar business.
Your job is to convert an unstructured support message into a safe, structured triage record.

Rules:
1. Never claim a payment is successful unless a source system has verified it.
2. Never authorize refunds, credits, account ownership changes, or customer-detail changes.
3. Flag fraud, safety, identity changes, low confidence, repeated service failures, and unclear messages for human review.
4. Keep the response draft short, respectful, and easy to understand.
5. Do not expose personal data unnecessarily.
6. Return only valid JSON with exactly these keys:
summary, category, priority, owner_team, recommended_action, response_draft, confidence, needs_human_review, reason.
Priority must be one of: Low, Medium, High, Urgent.
confidence must be a number from 0 to 1.
"""


def llm_triage(message: str, market: str, channel: str) -> TriageResult:
    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL")
    api_url = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")
    if not api_key or not model:
        raise RuntimeError("LLM_API_KEY and LLM_MODEL are required for LLM mode.")
    payload = {"model": model, "temperature": 0.1, "response_format": {"type": "json_object"}, "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": json.dumps({"market": market, "channel": channel, "message": _mask_pii(message)})}]}
    resp = requests.post(api_url, headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, json=payload, timeout=30)
    resp.raise_for_status()
    data = json.loads(resp.json()["choices"][0]["message"]["content"])
    required = set(TriageResult.__dataclass_fields__.keys())
    missing = required - set(data)
    if missing:
        raise ValueError(f"LLM response missing fields: {sorted(missing)}")
    return TriageResult(summary=str(data["summary"]), category=str(data["category"]), priority=str(data["priority"]), owner_team=str(data["owner_team"]), recommended_action=str(data["recommended_action"]), response_draft=str(data["response_draft"]), confidence=float(data["confidence"]), needs_human_review=bool(data["needs_human_review"]), reason=str(data["reason"]))


def triage_message(message: str, market: str = "Unknown", channel: str = "Unknown", mode: str = "demo") -> TriageResult:
    if mode == "llm":
        return llm_triage(message, market, channel)
    return heuristic_triage(message, market, channel)
