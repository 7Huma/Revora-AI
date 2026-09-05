from types import SimpleNamespace

from app.agents.recovery_executor import execute_intervention


class FakePaymentGateway:
    def retry(self, amount):
        return {
            "status": "success",
            "amount": amount,
        }


class FakeEmailClient:
    def send(self, subject, body):
        return {
            "status": "sent",
            "subject": subject,
            "body": body,
        }


def make_case(source, amount=1000.0):
    return SimpleNamespace(
        id="case-123",
        source=source,
        amount_at_risk=amount,
    )


def test_payment_failure_executes_payment_retry():
    result = execute_intervention(
        make_case("payment_failure"),
        payment_gateway=FakePaymentGateway(),
        email_client=FakeEmailClient(),
    )

    assert result["status"] == "recovery_attempted"
    assert result["action"] == "retry_payment"
    assert result["channel"] == "payment_gateway"
    assert result["result"]["status"] == "success"


def test_mandate_retry_uses_payment_gateway():
    result = execute_intervention(
        make_case("mandate_retry"),
        payment_gateway=FakePaymentGateway(),
        email_client=FakeEmailClient(),
    )

    assert result["action"] == "retry_mandate"
    assert result["channel"] == "payment_gateway"


def test_checkout_abandonment_sends_email():
    result = execute_intervention(
        make_case("checkout_abandonment"),
        payment_gateway=FakePaymentGateway(),
        email_client=FakeEmailClient(),
    )

    assert result["action"] == "send_checkout_recovery"
    assert result["channel"] == "email"
    assert result["result"]["status"] == "sent"


def test_subscription_failure_sends_email():
    result = execute_intervention(
        make_case("subscription_failure"),
        payment_gateway=FakePaymentGateway(),
        email_client=FakeEmailClient(),
    )

    assert result["action"] == "subscription_recovery"
    assert result["channel"] == "email"


def test_overdue_invoice_sends_email():
    result = execute_intervention(
        make_case("overdue_invoice", 5000.0),
        payment_gateway=FakePaymentGateway(),
        email_client=FakeEmailClient(),
    )

    assert result["action"] == "receivables_chase"
    assert result["channel"] == "email"


def test_unknown_source_requires_manual_review():
    result = execute_intervention(
        make_case("unknown"),
        payment_gateway=FakePaymentGateway(),
        email_client=FakeEmailClient(),
    )

    assert result["action"] == "manual_review"
    assert result["channel"] == "system"
    assert result["result"]["status"] == "manual_review_required"


def test_custom_channel_is_respected():
    result = execute_intervention(
        make_case("checkout_abandonment"),
        channel="WHATSAPP",
        payment_gateway=FakePaymentGateway(),
        email_client=FakeEmailClient(),
    )

    assert result["channel"] == "WHATSAPP"


def test_amount_is_passed_to_payment_gateway():
    result = execute_intervention(
        make_case("payment_failure", 7500.0),
        payment_gateway=FakePaymentGateway(),
        email_client=FakeEmailClient(),
    )

    assert result["result"]["amount"] == 7500.0