from app.agents.revenue_agent import analyze_case

def test_payment_recovery_decision():
    result = analyze_case("payment_failure", 5000, {"failure_reason": "insufficient_funds"})
    assert result["recommended_action"] == "retry_payment"
