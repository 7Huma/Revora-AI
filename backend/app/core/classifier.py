from app.db.models import RootCauseCategory


def analyze_root_cause(
    event_type: str,
    failure_code: str = "",
    failure_description: str = "",
) -> dict:
    """
    Deterministic Root Cause Analysis Engine.

    Detects the likely cause of revenue loss and returns:
    - root cause
    - reason
    - risk score
    - recommended recovery action

    This interface can later be backed by an LLM without
    changing the downstream recovery pipeline.
    """

    event_type = (event_type or "").strip().lower()
    failure_code = (failure_code or "").strip().upper()
    failure_description = (failure_description or "").strip().upper()

    # ---------------------------------------------------------
    # 1. PAYMENT FAILURE
    # ---------------------------------------------------------
    if event_type == "payment.failed":

        # Bank/payment gateway timeout
        if (
            "TIMEOUT" in failure_code
            or "TIMED_OUT" in failure_code
            or "TIMEOUT" in failure_description
            or "TIMED_OUT" in failure_description
        ):
            return {
                "root_cause": RootCauseCategory.PAYMENT_GATEWAY,
                "reason_detail": "BANK_SERVER_TIMEOUT",
                "risk_score": 35.0,
                "suggested_action": "INSTANT_UPI_FALLBACK",
            }

        # Insufficient balance
        if (
            "INSUFFICIENT" in failure_code
            or "BALANCE" in failure_code
            or "INSUFFICIENT" in failure_description
            or "BALANCE" in failure_description
        ):
            return {
                "root_cause": RootCauseCategory.PAYMENT_GATEWAY,
                "reason_detail": "INSUFFICIENT_FUNDS",
                "risk_score": 75.0,
                "suggested_action": "SCHEDULED_PAYMENT_NUDGE",
            }

        # Generic payment failure
        return {
            "root_cause": RootCauseCategory.PAYMENT_GATEWAY,
            "reason_detail": "GENERIC_DECLINE",
            "risk_score": 50.0,
            "suggested_action": "GENERIC_FALLBACK_LINK",
        }

    # ---------------------------------------------------------
    # 2. SUBSCRIPTION FAILURE
    # ---------------------------------------------------------
    if event_type == "subscription.halted":
        return {
            "root_cause": RootCauseCategory.SUBSCRIPTION_FAILED,
            "reason_detail": "RECURRING_MANDATE_DECLINED",
            "risk_score": 60.0,
            "suggested_action": "RE_AUTHORIZE_MANDATE_LINK",
        }

    # ---------------------------------------------------------
    # 3. CHECKOUT ABANDONMENT
    # ---------------------------------------------------------
    if event_type == "checkout.abandoned":
        return {
            "root_cause": RootCauseCategory.CHECKOUT_DROP_OFF,
            "reason_detail": "CART_ABANDONMENT",
            "risk_score": 50.0,
            "suggested_action": "DISCOUNT_INCENTIVE_NUDGE",
        }

    # ---------------------------------------------------------
    # 4. OVERDUE B2B RECEIVABLE
    # ---------------------------------------------------------
    if event_type in {
        "invoice.overdue",
        "receivable.overdue",
    }:
        return {
            "root_cause": RootCauseCategory.INVOICE_OVERDUE,
            "reason_detail": "OVERDUE_RECEIVABLE",
            "risk_score": 80.0,
            "suggested_action": "B2B_RECEIVABLES_FOLLOWUP",
        }

    # ---------------------------------------------------------
    # 5. SAFE DEFAULT
    # ---------------------------------------------------------
    return {
        "root_cause": RootCauseCategory.PAYMENT_GATEWAY,
        "reason_detail": "GENERIC_DECLINE",
        "risk_score": 50.0,
        "suggested_action": "GENERIC_FALLBACK_LINK",
    }