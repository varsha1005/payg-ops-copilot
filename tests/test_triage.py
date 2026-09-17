from src.triage import heuristic_triage


def test_payment_not_reflected_is_high_priority():
    result = heuristic_triage("I paid by mobile money but it is not showing and the system is still locked.")
    assert result.category == "Payment not reflected"
    assert result.priority == "High"
    assert result.needs_human_review is True


def test_agent_login_routes_to_internal_tools():
    result = heuristic_triage("Agent cannot login to the app and password reset failed.")
    assert result.category == "Agent app / access issue"
    assert result.owner_team == "Internal Tools Support"


def test_unclear_message_requires_review():
    result = heuristic_triage("Please help with this customer case.")
    assert result.category == "Other / needs review"
    assert result.needs_human_review is True


def test_fraud_keyword_forces_urgent_review():
    result = heuristic_triage("Customer says a fake agent asked for money and this looks like a scam.")
    assert result.category == "Payment / risk concern"
    assert result.priority == "Urgent"
    assert result.needs_human_review is True


def test_pii_is_masked_in_summary():
    result = heuristic_triage("Payment not showing. Call me on +254 712 345 678.")
    assert "+254" not in result.summary


def test_safety_issue_is_urgent_and_human_reviewed():
    result = heuristic_triage("The battery is very hot and started producing smoke.")
    assert result.category == "Product safety issue"
    assert result.priority == "Urgent"
    assert result.needs_human_review is True


def test_delivery_issue_routes_to_logistics():
    result = heuristic_triage("The solar kit was delivered but the package is missing one light.")
    assert result.category == "Delivery / missing component"
    assert result.owner_team == "Logistics / Customer Operations"


def test_warranty_request_requires_human_review():
    result = heuristic_triage("The battery stopped working again. Is it under warranty and can it be replaced?")
    assert result.category == "Warranty / replacement request"
    assert result.needs_human_review is True


def test_repeat_failure_is_high_priority():
    result = heuristic_triage("The solar unit failed for the third time after two technician visits.")
    assert result.category == "Repeat product failure"
    assert result.priority == "High"
    assert result.needs_human_review is True
