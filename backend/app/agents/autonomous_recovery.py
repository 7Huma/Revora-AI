from typing import Any

from app.services.recovery_service import execute_case


# Fallback actions if the first intervention fails.
FALLBACK_ACTIONS = {
    "payment_failure": "manual_review",
    "checkout_abandonment": "send_checkout_recovery",
    "subscription_failure": "subscription_recovery",
    "overdue_invoice": "receivables_chase",
    "mandate_retry": "manual_review",
}


def risk_label(risk_score: float) -> str:
    if risk_score >= 70:
        return "HIGH"

    if risk_score >= 40:
        return "MEDIUM"

    return "LOW"


def autonomous_recovery_agent(
    db,
    case: Any,
    channel: str | None = None,
) -> dict:
    """
    Autonomous recovery agent.

    Flow:

        ANALYZE
            ↓
        DECIDE
            ↓
        EXECUTE
            ↓
        EVALUATE
            ↓
        NEXT ACTION
    """

    # ============================================================
    # STEP 1 — ANALYZE
    # ============================================================

    risk = float(case.risk_score or 0)

    amount = float(
        case.amount_at_risk or 0
    )

    root_cause = str(
        case.root_cause.value
        if hasattr(case.root_cause, "value")
        else case.root_cause or "UNKNOWN"
    )

    source = str(
        case.source or "unknown"
    )

    suggested_action = str(
        case.suggested_action or "manual_review"
    )

    analysis = {
        "risk_score": risk,
        "risk_level": risk_label(risk),
        "amount_at_risk": amount,
        "root_cause": root_cause,
        "source": source,
    }

    # ============================================================
    # STEP 2 — DECIDE
    # ============================================================

    selected_action = suggested_action

    decision = {
        "selected_action": selected_action,
        "reason": (
            f"Selected "
            f"{selected_action.replace('_', ' ')} "
            f"for "
            f"{source.replace('_', ' ')} "
            f"with "
            f"{risk_label(risk)} "
            f"risk."
        ),
    }

    # ============================================================
    # STEP 3 — EXECUTE
    # ============================================================

    execution = execute_case(
        db=db,
        case=case,
        channel=channel,
    )

    # ------------------------------------------------------------
    # IMPORTANT:
    #
    # execute_case() already knows whether the intervention
    # succeeded and how much revenue was recovered.
    #
    # Do not independently infer success from a nested provider
    # response because that can disagree with the persisted case.
    # ------------------------------------------------------------

    execution_result = execution.get(
        "result",
        {},
    )

    if not isinstance(
        execution_result,
        dict,
    ):
        execution_result = {}

    # Primary success signal.
    success = bool(
        execution_result.get(
            "success",
            False,
        )
    )

    # execute_case() also returns recovered_amount.
    recovered_amount = float(
        execution.get(
            "recovered_amount",
            0,
        )
        or 0
    )

    # If money was actually recovered, the intervention
    # is successful even if a provider omitted `success`.
    if recovered_amount > 0:
        success = True

    # Persisted case status is the final source of truth.
    case_status = (
        case.status.value
        if hasattr(
            case.status,
            "value",
        )
        else str(
            case.status or ""
        )
    )

    case_status = case_status.upper()

    if case_status == "RECOVERED":
        success = True

    # ============================================================
    # STEP 4 — EVALUATE
    # ============================================================

    if success:
        outcome = "SUCCESS"

        # A successful recovery should never exceed the
        # original at-risk amount.
        recovered_amount = min(
            recovered_amount or amount,
            amount,
        )

    else:
        outcome = "FAILED"

        recovered_amount = 0.0

    recovery_rate = (
        round(
            recovered_amount / amount,
            2,
        )
        if amount > 0
        else 0
    )

    # ============================================================
    # STEP 5 — NEXT ACTION
    # ============================================================

    if success:

        next_action = {
            "action": "close_case",
            "reason": (
                "Revenue was successfully recovered. "
                "The case can now be closed."
            ),
        }

    else:

        fallback = FALLBACK_ACTIONS.get(
            source,
            "manual_review",
        )

        next_action = {
            "action": fallback,
            "reason": (
                "The initial recovery intervention failed. "
                "The agent recommends a fallback action "
                "instead of repeating the same intervention."
            ),
        }

    # ============================================================
    # FINAL EVALUATION
    # ============================================================

    evaluation = {
        "outcome": outcome,
        "success": success,
        "recovered_amount": recovered_amount,
        "recovery_rate": recovery_rate,
        "case_status": case_status,
        "next_action": next_action["action"],
    }

    # ============================================================
    # COMPLETE AUTONOMOUS TRACE
    # ============================================================

    return {
        "success": True,

        "agent": {
            "status": "completed",
            "mode": "autonomous",
        },

        "case": {
            "id": case.id,
            "customer_id": case.customer_id,
            "source": source,
        },

        "analysis": analysis,

        "decision": decision,

        "execution": execution,

        "evaluation": evaluation,

        "outcome": {
            "outcome": outcome,
            "recovered_amount": recovered_amount,
            "recovery_rate": recovery_rate,
            "next_action": next_action["action"],
            "learning_signal": (
                "positive"
                if success
                else "negative"
            ),
        },

        "next_action": next_action["action"],

        "agent_loop": [
            "ANALYZE",
            "DECIDE",
            "EXECUTE",
            "EVALUATE",
            "NEXT_ACTION",
        ],
    }