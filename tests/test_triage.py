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
    result = heuristic_triage("Customer says agent took cash and this looks like fraud.")
    assert result.priority == "Urgent"
    assert result.needs_human_review is True


def test_pii_is_masked_in_summary():
    result = heuristic_triage("Payment not showing. Call me on +254 712 345 678.")
    assert "+254" not in result.summary
