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


CATEGORY_RULES = [
    (
        "Payment not reflected",
        ["paid", "payment", "mpesa", "m-pesa", "mobile money", "money sent", "transaction", "receipt"],
        ["not reflect", "not showing", "missing", "still locked", "not updated", "not credited", "code not"],
    ),
    (
        "Unlock code issue",
        ["unlock", "code", "token", "keypad"],
        ["not received", "not working", "invalid", "wrong", "failed", "no code"],
    ),
    (
        "Device / product issue",
        ["solar", "battery", "lamp", "light", "panel", "fan", "tv", "device", "system"],
        ["not working", "dead", "off", "won't turn", "wont turn", "fault", "broken", "stopped", "no power"],
    ),
    (
        "Installation / service delay",
        ["install", "technician", "service", "visit", "appointment"],
        ["delay", "waiting", "did not come", "not come", "late", "reschedule", "pending"],
    ),
    (
        "Agent app / access issue",
        ["agent", "app", "login", "password", "otp", "account", "sync"],
        ["cannot", "can't", "cant", "failed", "locked", "error", "not syncing", "unable"],
    ),
    (
        "Customer details update",
        ["phone", "number", "name", "details", "contact"],
        ["change", "update", "wrong", "new number", "edit"],
    ),
    (
        "Payment plan / balance query",
        ["balance", "remaining", "installment", "instalment", "weekly", "payment plan", "due", "payoff"],
        ["how much", "when", "remaining", "due", "balance", "early"],
    ),
]


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
    confidence = 0.58
    for name, context_terms, problem_terms in CATEGORY_RULES:
        if _contains_any(text, context_terms) and _contains_any(text, problem_terms):
            category = name
            confidence = 0.86
            break

    fraud_terms = ["fraud", "stolen", "cash missing", "agent took", "scam", "threat", "unsafe"]
    vulnerable_terms = ["hospital", "clinic", "medical", "school", "emergency"]

    if _contains_any(text, fraud_terms):
        priority = "Urgent"
        owner = "Risk / Operations"
        human = True
        confidence = max(confidence, 0.92)
        reason = "Potential fraud, safety, or cash-handling risk requires immediate human review."
    elif category in {"Payment not reflected", "Unlock code issue"}:
        priority = "High"
        owner = "Payments / Customer Operations"
        human = True
        reason = "Payment or access issue may interrupt product use; verify against source systems before responding."
    elif category == "Device / product issue":
        priority = "High" if _contains_any(text, vulnerable_terms) else "Medium"
        owner = "Service Operations"
        human = priority == "High"
        reason = "Potential service interruption; priority is higher where essential services may be affected."
    elif category == "Installation / service delay":
        priority = "Medium"
        owner = "Field Service Operations"
        human = False
        reason = "Needs scheduling/status verification and field-team follow-up."
    elif category == "Agent app / access issue":
        priority = "Medium"
        owner = "Internal Tools Support"
        human = False
        reason = "Agent productivity issue; route to internal tools support with account context."
    elif category == "Customer details update":
        priority = "Medium"
        owner = "Customer Operations"
        human = True
        reason = "Personal-data changes should be verified before modification."
    elif category == "Payment plan / balance query":
        priority = "Low"
        owner = "Customer Support"
        human = False
        reason = "Routine account query; answer only after retrieving verified account data."
    else:
        priority = "Medium"
        owner = "Customer Operations"
        human = True
        reason = "Intent is not clear enough for safe automation."

    safe_text = _mask_pii(raw)
    summary = safe_text[:180] + ("..." if len(safe_text) > 180 else "")

    action_map = {
        "Payment not reflected": "Check transaction reference and payment ledger; confirm whether payment posted; resend or regenerate access code only after verification.",
        "Unlock code issue": "Verify latest successful payment and code status; resend valid code or escalate if code generation failed.",
        "Device / product issue": "Run basic troubleshooting checklist; verify warranty/service status; create technician visit if unresolved.",
        "Installation / service delay": "Check appointment/installer status, propose next available slot, and notify the field coordinator if overdue.",
        "Agent app / access issue": "Validate agent ID and account status; attempt password/OTP recovery; escalate persistent sync or authentication errors.",
        "Customer details update": "Verify customer identity using approved process before updating contact or account details.",
        "Payment plan / balance query": "Retrieve verified balance/plan details from the account system and explain the next due amount/date in simple language.",
        "Other / needs review": "Ask one clarifying question, then route to the relevant operations owner. Do not take account-changing action automatically.",
    }
    recommended_action = action_map[category]

    response_draft = (
        "Thanks for reporting this. I have captured the issue and routed it to the right team. "
        "We will first verify the account/payment details before making any changes. "
        "Please keep your transaction reference or customer ID available if the support team asks for it."
    )

    return TriageResult(
        summary=summary,
        category=category,
        priority=priority,
        owner_team=owner,
        recommended_action=recommended_action,
        response_draft=response_draft,
        confidence=round(confidence, 2),
        needs_human_review=human or confidence < 0.75,
        reason=reason,
    )


SYSTEM_PROMPT = """You are an operations triage assistant for a PAYG solar business.
Your job is to convert an unstructured support message into a safe, structured triage record.

Rules:
1. Never claim a payment is successful unless a source system has verified it.
2. Never authorize refunds, credits, account ownership changes, or customer-detail changes.
3. Flag fraud, safety, identity changes, low confidence, and unclear messages for human review.
4. Keep the response draft short, respectful, and easy to understand.
5. Do not expose personal data unnecessarily.
6. Return only valid JSON with exactly these keys:
summary, category, priority, owner_team, recommended_action, response_draft, confidence, needs_human_review, reason.
Priority must be one of: Low, Medium, High, Urgent.
confidence must be a number from 0 to 1.
"""


def llm_triage(message: str, market: str, channel: str) -> TriageResult:
    """Call an OpenAI-compatible chat-completions endpoint.

    Environment variables:
      LLM_API_KEY      required
      LLM_API_URL      default: https://api.openai.com/v1/chat/completions
      LLM_MODEL        required for real LLM mode

    This adapter is intentionally small so the prototype can be swapped to another
    provider in production without changing the product workflow.
    """
    api_key = os.getenv("LLM_API_KEY")
    model = os.getenv("LLM_MODEL")
    api_url = os.getenv("LLM_API_URL", "https://api.openai.com/v1/chat/completions")

    if not api_key or not model:
        raise RuntimeError("LLM_API_KEY and LLM_MODEL are required for LLM mode.")

    payload = {
        "model": model,
        "temperature": 0.1,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": json.dumps({"market": market, "channel": channel, "message": _mask_pii(message)}),
            },
        ],
    }
    resp = requests.post(
        api_url,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    content = resp.json()["choices"][0]["message"]["content"]
    data = json.loads(content)

    required = set(TriageResult.__dataclass_fields__.keys())
    missing = required - set(data)
    if missing:
        raise ValueError(f"LLM response missing fields: {sorted(missing)}")

    return TriageResult(
        summary=str(data["summary"]),
        category=str(data["category"]),
        priority=str(data["priority"]),
        owner_team=str(data["owner_team"]),
        recommended_action=str(data["recommended_action"]),
        response_draft=str(data["response_draft"]),
        confidence=float(data["confidence"]),
        needs_human_review=bool(data["needs_human_review"]),
        reason=str(data["reason"]),
    )


def triage_message(message: str, market: str = "Unknown", channel: str = "Unknown", mode: str = "demo") -> TriageResult:
    if mode == "llm":
        return llm_triage(message, market, channel)
    return heuristic_triage(message, market, channel)
