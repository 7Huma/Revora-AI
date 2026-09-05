from datetime import datetime
from typing import Any

from app.integrations.payment_gateway import PaymentGateway
from app.integrations.email import EmailClient


ACTION_MAP = {
    "payment_failure": "retry_payment",
    "checkout_abandonment": "send_checkout_recovery",
    "subscription_failure": "subscription_recovery",
    "overdue_invoice": "receivables_chase",
    "mandate_retry": "retry_mandate",
}


def calculate_recovery_probability(case: Any) -> float:
    """
    Deterministic recovery probability for the demo.

    This gives the autonomous agent a confidence signal
    that it can use when deciding whether to automate,
    retry, or escalate.
    """

    source = str(
        case.source or ""
    ).lower()

    risk = float(
        case.risk_score or 0
    )

    base_probability = {
        "payment_failure": 0.82,
        "checkout_abandonment": 0.58,
        "subscription_failure": 0.74,
        "overdue_invoice": 0.68,
        "mandate_retry": 0.78,
    }.get(source, 0.50)

    risk_adjustment = (
        70 - risk
    ) * 0.002

    probability = (
        base_probability
        + risk_adjustment
    )

    return round(
        max(
            0.05,
            min(
                0.95,
                probability,
            ),
        ),
        2,
    )


def select_intervention(case: Any) -> dict:
    """
    Autonomous decision layer.

    The agent decides:
    - what action to take
    - which channel to use
    - why it selected that action
    """

    source = str(
        case.source or ""
    ).lower()

    risk = float(
        case.risk_score or 0
    )

    probability = (
        calculate_recovery_probability(case)
    )

    # ------------------------------------------------------------
    # Payment failure
    # ------------------------------------------------------------

    if source == "payment_failure":

        return {
            "action": "retry_payment",
            "channel": "payment_gateway",
            "reason": (
                "The payment failure is potentially "
                "recoverable automatically. The agent "
                "will attempt a payment retry before "
                "escalating to customer outreach."
            ),
            "probability": probability,
        }

    # ------------------------------------------------------------
    # Mandate retry
    # ------------------------------------------------------------

    if source == "mandate_retry":

        return {
            "action": "retry_mandate",
            "channel": "payment_gateway",
            "reason": (
                "The recurring mandate can potentially "
                "be recovered through an automated retry."
            ),
            "probability": probability,
        }

    # ------------------------------------------------------------
    # Checkout abandonment
    # ------------------------------------------------------------

    if source == "checkout_abandonment":

        return {
            "action": "send_checkout_recovery",
            "channel": "email",
            "reason": (
                "The customer demonstrated purchase intent "
                "by starting checkout. A targeted recovery "
                "message is the lowest-friction intervention."
            ),
            "probability": probability,
        }

    # ------------------------------------------------------------
    # Subscription failure
    # ------------------------------------------------------------

    if source == "subscription_failure":

        return {
            "action": "subscription_recovery",
            "channel": "email",
            "reason": (
                "The subscription is at risk of becoming "
                "lost recurring revenue. The agent will "
                "attempt automated recovery before escalation."
            ),
            "probability": probability,
        }

    # ------------------------------------------------------------
    # Overdue invoice
    # ------------------------------------------------------------

    if source == "overdue_invoice":

        return {
            "action": "receivables_chase",
            "channel": "email",
            "reason": (
                "This is an outstanding receivable. "
                "A targeted payment follow-up is more "
                "appropriate than an automatic payment retry."
            ),
            "probability": probability,
        }

    # ------------------------------------------------------------
    # Unknown case
    # ------------------------------------------------------------

    return {
        "action": "manual_review",
        "channel": "system",
        "reason": (
            "The case does not match a supported "
            "automated recovery strategy."
        ),
        "probability": probability,
    }


def execute_intervention(
    case: Any,
    channel: str | None = None,
    payment_gateway: Any | None = None,
    email_client: Any | None = None,
) -> dict:
    """
    Execute the intervention selected by the autonomous recovery agent.

    External integrations can be injected during testing.
    """

    payment_gateway = payment_gateway or PaymentGateway()
    email_client = email_client or EmailClient()

    decision = select_intervention(case)

    action = decision["action"]
    selected_channel = channel or decision["channel"]

    # PAYMENT RETRY
    if action == "retry_payment":
        result = payment_gateway.retry(case.amount_at_risk)

    # MANDATE RETRY
    elif action == "retry_mandate":
        result = payment_gateway.retry(case.amount_at_risk)

    # EMAIL RECOVERY
    elif action in {
        "send_checkout_recovery",
        "subscription_recovery",
        "receivables_chase",
    }:
        result = email_client.send(
            subject=f"Recovery follow-up for case #{case.id}",
            body=(
                "We are following up regarding a payment "
                f"of {case.amount_at_risk:.2f}."
            ),
        )

    # MANUAL REVIEW
    else:
        result = {
            "status": "manual_review_required",
            "success": False,
        }

    if not isinstance(result, dict):
        result = {
            "status": "completed",
            "success": bool(result),
            "raw_result": result,
        }

    success = bool(result.get("success", False))

    # Demo integrations may return a status instead of success.
    if (
        "success" not in result
        and str(result.get("status", "")).lower()
        in {
            "sent",
            "success",
            "succeeded",
            "recovered",
            "completed",
        }
    ):
        success = True

    return {
        "case_id": case.id,

        "analysis": {
            "risk_score": case.risk_score,
            "root_cause": (
                case.root_cause.value
                if hasattr(case.root_cause, "value")
                else case.root_cause
            ),
            "suggested_action": case.suggested_action,
        },

        "execution": result,
        "result": result,
        "success": success,
        "action": action,
        "channel": selected_channel,
        "probability": decision["probability"],
        "decision_reason": decision["reason"],
        "executed_at": datetime.utcnow().isoformat(),
    }

def run_autonomous_recovery(
    case: Any,
    payment_gateway: Any | None = None,
    email_client: Any | None = None,
) -> dict:
    """
    Autonomous Recovery Agent.

    Flow:

        DETECT
          ↓
        DIAGNOSE
          ↓
        DECIDE
          ↓
        ACT
          ↓
        OBSERVE
          ↓
        ESCALATE / COMPLETE
    """

    decision = select_intervention(
        case
    )

    probability = decision[
        "probability"
    ]

    risk = float(
        case.risk_score or 0
    )

    # ============================================================
    # AGENT DECISION
    # ============================================================

    if decision["action"] == "manual_review":

        return {
            "agent_status":
                "ESCALATED",

            "stage":
                "ESCALATION",

            "action":
                "manual_review",

            "channel":
                "system",

            "probability":
                probability,

            "risk_score":
                risk,

            "decision_reason":
                decision["reason"],

            "message":
                "Case escalated to manual review.",

            "executed_at":
                datetime.utcnow().isoformat(),
        }

    # ============================================================
    # EXECUTE
    # ============================================================

    execution = execute_intervention(
        case=case,
        payment_gateway=payment_gateway,
        email_client=email_client,
    )

    success = execution[
        "success"
    ]

    # ============================================================
    # OBSERVE OUTCOME
    # ============================================================

    if success:

        return {
            **execution,

            "agent_status":
                "RECOVERED",

            "stage":
                "COMPLETED",

            "next_action":
                "close_case",

            "message":
                "Revenue successfully recovered.",

            "recovered_amount":
                float(
                    case.amount_at_risk
                ),

            "remaining_risk":
                0.0,
        }

    # ============================================================
    # FAILED FIRST ATTEMPT
    # ============================================================

    return {
        **execution,

        "agent_status":
            "ESCALATED",

        "stage":
            "ESCALATION",

        "next_action":
            "manual_review",

        "message":
            "Initial recovery attempt failed. "
            "Case requires escalation.",

        "recovered_amount":
            0.0,

        "remaining_risk":
            float(
                case.amount_at_risk
            ),
    }