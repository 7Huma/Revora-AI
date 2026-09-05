from app.agents.risk_detector import calculate_risk

def test_high_value_failed_payment_is_high_risk():
    result = calculate_risk("payment_failure", 50000, {"previous_failures": 1, "customer_ltv": 50000})
    assert result["score"] >= 70
