from datetime import datetime

from app.agents.recovery_executor import execute_intervention
from app.core.classifier import analyze_root_cause
from app.db.models import (
    RecoveryCase,
    RecoveryCaseStatus,
    Intervention,
)


# ============================================================
# AI RECOVERY INTELLIGENCE
# ============================================================

def build_ai_intelligence(
    source,
    amount,
    risk_score,
    root_cause,
    suggested_action,
    recovery_probability,
):
    """
    Generate the explainable intelligence used by the
    AI Recovery Agent.

    This is deterministic for the hackathon demo so that
    the same case always produces a consistent decision.
    """

    source = str(source or "").lower()

    amount = float(amount or 0)

    risk_score = float(risk_score or 0)

    root_cause = str(
        root_cause.value
        if hasattr(root_cause, "value")
        else root_cause or ""
    ).replace("_", " ")

    suggested_action = str(
        suggested_action or "manual_review"
    ).replace("_", " ")

    recovery_probability = float(
        recovery_probability or 0
    )

    # --------------------------------------------------------
    # Priority
    # --------------------------------------------------------

    if risk_score >= 70:
        priority = "HIGH"
    elif risk_score >= 40:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    # --------------------------------------------------------
    # Recovery probability
    # --------------------------------------------------------

    probability_percent = round(
        recovery_probability * 100
    )

    expected_recovery = round(
        amount * recovery_probability,
        2,
    )

    # --------------------------------------------------------
    # Case-specific reasoning
    # --------------------------------------------------------

    if source == "overdue_invoice":

        why_now = (
            f"₹{amount:,.0f} is tied to an overdue "
            "B2B receivable, making the outstanding "
            "revenue immediately actionable."
        )

        signals = [
            "Invoice is overdue",
            "B2B receivable",
            f"₹{amount:,.0f} revenue exposure",
            f"Risk score: {risk_score:.0f}/100",
        ]

        why_action = (
            "A targeted receivables follow-up is preferred "
            "over an automatic payment retry because the "
            "revenue originates from an outstanding invoice."
        )

    elif source == "payment_failure":

        why_now = (
            f"A payment attempt failed and "
            f"₹{amount:,.0f} is currently at risk."
        )

        signals = [
            "Payment attempt failed",
            f"₹{amount:,.0f} revenue exposure",
            f"Root cause: {root_cause}",
            f"Risk score: {risk_score:.0f}/100",
        ]

        why_action = (
            "A payment recovery intervention is appropriate "
            "because the customer has already attempted to pay "
            "and the failed transaction may be recoverable."
        )

    elif source == "subscription_failure":

        why_now = (
            f"A recurring subscription payment failed, "
            f"putting ₹{amount:,.0f} of recurring revenue "
            "at risk."
        )

        signals = [
            "Recurring payment failed",
            "Subscription at risk",
            f"₹{amount:,.0f} revenue exposure",
            f"Root cause: {root_cause}",
        ]

        why_action = (
            "The selected intervention attempts to restore "
            "billing before the failed payment becomes "
            "subscription churn."
        )

    elif source == "checkout_abandonment":

        why_now = (
            f"The customer reached checkout but did not "
            f"complete payment, leaving ₹{amount:,.0f} "
            "of potentially recoverable revenue."
        )

        signals = [
            "Checkout started",
            "Payment not completed",
            f"₹{amount:,.0f} revenue exposure",
            "Customer still has purchase intent",
        ]

        why_action = (
            "A checkout recovery nudge is preferred because "
            "the customer has already demonstrated purchase "
            "intent and can potentially be brought back "
            "without manual intervention."
        )

    elif source == "mandate_retry":

        why_now = (
            f"A recurring mandate failed with "
            f"₹{amount:,.0f} at risk."
        )

        signals = [
            "Recurring mandate failed",
            f"₹{amount:,.0f} revenue exposure",
            f"Root cause: {root_cause}",
            "Retry opportunity exists",
        ]

        why_action = (
            "A mandate retry is appropriate because the "
            "billing relationship already exists and the "
            "failed recurring payment may be recovered."
        )

    else:

        why_now = (
            f"₹{amount:,.0f} has been identified as "
            "at-risk revenue."
        )

        signals = [
            f"₹{amount:,.0f} revenue exposure",
            f"Risk score: {risk_score:.0f}/100",
            f"Root cause: {root_cause}",
        ]

        why_action = (
            "The intervention was selected based on the "
            "detected revenue risk and root cause."
        )

    # --------------------------------------------------------
    # Build explainable AI output
    # --------------------------------------------------------

    return {
        "priority": priority,

        "why_now": why_now,

        "signals": signals,

        "recommended_action": suggested_action,

        "why_action": why_action,

        "recovery_probability": recovery_probability,

        "recovery_probability_percent": probability_percent,

        "expected_recovery": expected_recovery,

        "risk_score": risk_score,

        "root_cause": root_cause,
    }


# ============================================================
# CREATE RECOVERY CASE
# ============================================================

def create_case(
    db,
    customer_id,
    source,
    amount,
    context=None,
):
    """
    Create a persisted recovery case from an incoming
    revenue-risk event.
    """

    context = context or {}

    event_type = (
        context.get("event_type")
        or {
            "payment_failure": "payment.failed",
            "checkout_abandonment": "checkout.abandoned",
            "subscription_failure": "subscription.halted",
            "overdue_invoice": "invoice.overdue",
            "mandate_retry": "subscription.halted",
        }.get(
            source,
            "unknown.event",
        )
    )

    # --------------------------------------------------------
    # Diagnose root cause
    # --------------------------------------------------------

    diagnosis = analyze_root_cause(
        event_type=event_type,
        failure_code=context.get(
            "failure_code",
            "",
        ),
        failure_description=context.get(
            "failure_description",
            context.get(
                "failure_reason",
                "",
            ),
        ),
    )

    # --------------------------------------------------------
    # Calculate deterministic recovery probability
    #
    # Keep this aligned with the value used by the API
    # serializer so dashboard numbers remain consistent.
    # --------------------------------------------------------

    risk_score = float(
        diagnosis["risk_score"] or 0
    )

    base_probability = {
        "payment_failure": 0.82,
        "checkout_abandonment": 0.58,
        "subscription_failure": 0.74,
        "overdue_invoice": 0.68,
        "mandate_retry": 0.78,
    }.get(
        str(source).lower(),
        0.50,
    )

    risk_adjustment = (
        70 - risk_score
    ) * 0.002

    recovery_probability = round(
        max(
            0.05,
            min(
                0.95,
                base_probability
                + risk_adjustment,
            ),
        ),
        2,
    )

    # --------------------------------------------------------
    # AI intelligence
    # --------------------------------------------------------

    intelligence = build_ai_intelligence(
        source=source,
        amount=amount,
        risk_score=risk_score,
        root_cause=diagnosis["root_cause"],
        suggested_action=diagnosis[
            "suggested_action"
        ],
        recovery_probability=recovery_probability,
    )

    # --------------------------------------------------------
    # Create database case
    # --------------------------------------------------------

    case = RecoveryCase(
        customer_id=str(
            customer_id
        ),

        source=source,

        amount_at_risk=float(
            amount
        ),

        risk_score=risk_score,

        root_cause=diagnosis[
            "root_cause"
        ],

        reason_detail=diagnosis[
            "reason_detail"
        ],

        suggested_action=diagnosis[
            "suggested_action"
        ],

        agent_reason=(
            intelligence["why_now"]
            + " "
            + intelligence["why_action"]
        ),

        status=RecoveryCaseStatus.OPEN,

        created_at=datetime.utcnow(),
    )

    db.add(case)

    db.commit()

    db.refresh(case)

    return case, diagnosis


# ============================================================
# EXECUTE RECOVERY
# ============================================================

def execute_case(
    db,
    case,
    channel=None,
):
    """
    Execute and persist a recovery intervention.
    """

    result = execute_intervention(
        case,
        channel,
    )

    success = result.get(
        "result",
        {},
    ).get(
        "success",
        False,
    )

    # --------------------------------------------------------
    # Create intervention history
    # --------------------------------------------------------

    intervention = Intervention(
        recovery_case_id=case.id,

        type=result["action"],

        channel=result["channel"].upper(),

        message=(
            f"Recovery action executed "
            f"for case #{case.id}"
        ),

        executed_at=datetime.utcnow(),

        result=(
            "SUCCESS"
            if success
            else "FAILED"
        ),

        recovered_amount=(
            case.amount_at_risk
            if success
            else 0.0
        ),
    )

    db.add(intervention)

    # --------------------------------------------------------
    # Update case status
    # --------------------------------------------------------

    if success:
        case.status = (
            RecoveryCaseStatus.RECOVERED
        )
    else:
        case.status = (
            RecoveryCaseStatus.FAILED
        )

    db.commit()

    db.refresh(intervention)

    # --------------------------------------------------------
    # Return execution result
    # --------------------------------------------------------

    result["recovered_amount"] = (
        intervention.recovered_amount
    )

    result["case_status"] = (
        case.status.value
    )

    return result