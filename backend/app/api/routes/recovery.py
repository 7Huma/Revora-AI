from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.recovery_executor import (
    run_autonomous_recovery,
)
from app.db.models import (
    Intervention,
    RecoveryCase,
)
from app.db.database import get_db
from app.schemas.recovery import ExecuteRecovery
from app.services.recovery_service import execute_case

from fastapi import APIRouter, Depends, HTTPException

from app.db.models import RecoveryCase
from app.agents.autonomous_recovery import (
    autonomous_recovery_agent,
)

from app.agents.outcome_analyzer import (
    analyze_outcome,
)


router = APIRouter()


# ============================================================
# RECOVERY PROBABILITY
# ============================================================

def calculate_recovery_probability(case):
    """
    Demo recovery probability based on case characteristics.

    This is intentionally deterministic for the hackathon demo.
    """

    source = str(case.source or "").lower()
    risk = float(case.risk_score or 0)

    base_probability = {
        "payment_failure": 0.82,
        "checkout_abandonment": 0.58,
        "subscription_failure": 0.74,
        "overdue_invoice": 0.68,
        "mandate_retry": 0.78,
    }.get(source, 0.50)

    # Higher-risk cases receive slightly lower
    # recovery probability.
    risk_adjustment = (70 - risk) * 0.002

    probability = (
        base_probability + risk_adjustment
    )

    return round(
        max(
            0.05,
            min(0.95, probability),
        ),
        2,
    )


# ============================================================
# AI REASONING
# ============================================================

def ai_reasoning(x):
    """
    Generate a human-readable explanation of why
    the recovery agent selected the recommended action.
    """

    source = str(
        x.source or ""
    ).lower()

    root_cause = str(
        x.root_cause.value
        if hasattr(
            x.root_cause,
            "value",
        )
        else x.root_cause
    ).replace(
        "_",
        " ",
    )

    action = str(
        x.suggested_action
        or "manual review"
    ).replace(
        "_",
        " ",
    )

    amount = float(
        x.amount_at_risk or 0
    )

    risk = float(
        x.risk_score or 0
    )

    if source == "overdue_invoice":
        return (
            f"The invoice is overdue and represents "
            f"₹{amount:,.0f} of outstanding revenue. "
            f"Because this is a B2B receivable, the safest "
            f"recovery path is a targeted payment follow-up "
            f"rather than an automatic payment retry. "
            f"The case is high priority with a risk score of "
            f"{risk:.0f}/100."
        )

    if source == "payment_failure":
        return (
            f"A payment attempt failed, putting "
            f"₹{amount:,.0f} at risk. "
            f"The detected cause is {root_cause}. "
            f"The AI selected {action} because the payment "
            f"can potentially be recovered without manual "
            f"intervention."
        )

    if source == "subscription_failure":
        return (
            f"The subscription payment failed and "
            f"₹{amount:,.0f} is at risk of becoming lost "
            f"revenue. The detected cause is "
            f"{root_cause}. The AI recommends "
            f"{action} to restore billing before the "
            f"customer fully churns."
        )

    if source == "checkout_abandonment":
        return (
            f"The customer started checkout but did not "
            f"complete the payment, leaving "
            f"₹{amount:,.0f} at risk. "
            f"The AI recommends {action} to bring the "
            f"customer back to the payment flow."
        )

    if source == "mandate_retry":
        return (
            f"The recurring mandate failed, putting "
            f"₹{amount:,.0f} at risk. "
            f"The AI recommends {action} because the "
            f"mandate can be retried before escalating "
            f"to manual recovery."
        )

    return (
        f"₹{amount:,.0f} was identified as at-risk "
        f"revenue. The AI detected {root_cause} and "
        f"selected {action} based on the current "
        f"case risk."
    )


# ============================================================
# AI DECISION TRACE
# ============================================================

def decision_trace(x):
    """
    Build the explainable AI decision trail shown
    inside the Recovery Decision drawer.
    """

    probability = (
        calculate_recovery_probability(x)
    )

    amount = float(
        x.amount_at_risk or 0
    )

    risk = float(
        x.risk_score or 0
    )

    root_cause = str(
        x.root_cause.value
        if hasattr(
            x.root_cause,
            "value",
        )
        else x.root_cause
    ).replace(
        "_",
        " ",
    )

    action = str(
        x.suggested_action
        or "manual_review"
    ).replace(
        "_",
        " ",
    )

    if risk >= 70:
        priority = "HIGH"
    elif risk >= 40:
        priority = "MEDIUM"
    else:
        priority = "LOW"

    return [
        {
            "step": 1,
            "title": "Revenue risk detected",
            "detail": (
                f"₹{amount:,.0f} identified as "
                "at-risk revenue."
            ),
        },
        {
            "step": 2,
            "title": "Risk scored",
            "detail": (
                f"Risk score: {risk:.0f}/100 · "
                f"{priority} priority"
            ),
        },
        {
            "step": 3,
            "title": "Root cause diagnosed",
            "detail": root_cause,
        },
        {
            "step": 4,
            "title": "Recovery probability estimated",
            "detail": (
                f"AI estimates a "
                f"{round(probability * 100)}% "
                "probability of successful recovery."
            ),
        },
        {
            "step": 5,
            "title": "Intervention selected",
            "detail": action,
        },
    ]


# ============================================================
# SERIALIZE CASE
# ============================================================

def serialize_case(x):
    """
    Convert a RecoveryCase database object into
    the structure expected by the frontend.
    """

    probability = (
        calculate_recovery_probability(x)
    )

    amount_at_risk = float(
        x.amount_at_risk or 0
    )

    expected_recovery = round(
        amount_at_risk * probability,
        2,
    )

    return {
        "id": x.id,

        "customer_id": x.customer_id,

        "source": x.source,

        "amount_at_risk": x.amount_at_risk,

        "risk_score": x.risk_score,

        "root_cause": (
            x.root_cause.value
            if hasattr(
                x.root_cause,
                "value",
            )
            else x.root_cause
        ),

        "status": (
            x.status.value
            if hasattr(
                x.status,
                "value",
            )
            else x.status
        ),

        # Human-readable AI explanation
        "reason":  x.reason_detail,

        "reason_detail": x.reason_detail,

        # Used by the frontend AI reasoning section
        "agent_reason": ai_reasoning(x),

        "suggested_action": x.suggested_action,

        "recovery_probability": probability,

        "expected_recovery": expected_recovery,

        "ai_intelligence": {
    "priority": (
        "HIGH"
        if float(x.risk_score or 0) >= 70
        else "MEDIUM"
        if float(x.risk_score or 0) >= 40
        else "LOW"
    ),

    "why_now": ai_reasoning(x),

    "signals": [
        f"₹{float(x.amount_at_risk or 0):,.0f} revenue exposure",
        f"Risk score: {float(x.risk_score or 0):.0f}/100",
        (
            str(
                x.root_cause.value
                if hasattr(
                    x.root_cause,
                    "value",
                )
                else x.root_cause
            ).replace("_", " ")
        ),
    ],

    "recommended_action": (
        str(
            x.suggested_action
            or "manual_review"
        ).replace("_", " ")
    ),

    "why_action": ai_reasoning(x),

    "recovery_probability": probability,

    "expected_recovery": expected_recovery,
},
        # Explainable AI decision trail
        "decision_trace": decision_trace(x),

        "created_at": x.created_at,
    }


# ============================================================
# GET ALL RECOVERY CASES
# ============================================================

@router.get("/cases")
def cases(
    db: Session = Depends(get_db),
):
    rows = (
        db.query(RecoveryCase)
        .order_by(
            RecoveryCase.created_at.desc()
        )
        .all()
    )

    return [
        serialize_case(x)
        for x in rows
    ]


# ============================================================
# GET SINGLE RECOVERY CASE
# ============================================================

@router.get("/cases/{case_id}")
def get_case(
    case_id: str,
    db: Session = Depends(get_db),
):
    case = db.get(
        RecoveryCase,
        case_id,
    )

    if not case:
        raise HTTPException(
            404,
            "Recovery case not found",
        )

    return serialize_case(case)


# ============================================================
# EXECUTE RECOVERY
# ============================================================

@router.post("/execute/{case_id}")
def execute(
    case_id: str,
    payload: ExecuteRecovery | None = None,
    db: Session = Depends(get_db),
):
    case = db.get(
        RecoveryCase,
        case_id,
    )

    if not case:
        raise HTTPException(
            404,
            "Recovery case not found",
        )

    return execute_case(
        db,
        case,
        payload.channel
        if payload
        else None,
    )


# ============================================================
# INTERVENTION HISTORY
# ============================================================

@router.get(
    "/cases/{case_id}/interventions"
)
def get_intervention_history(
    case_id: str,
    db: Session = Depends(get_db),
):
    # Make sure the case exists
    case = db.get(
        RecoveryCase,
        case_id,
    )

    if not case:
        raise HTTPException(
            404,
            "Recovery case not found",
        )

    interventions = (
        db.query(Intervention)
        .filter(
            Intervention.recovery_case_id
            == case_id
        )
        .order_by(
            Intervention.executed_at.desc()
        )
        .all()
    )

    return [
        {
            "id": intervention.id,

            "type": intervention.type,

            "channel": (
                intervention.channel.value
                if hasattr(
                    intervention.channel,
                    "value",
                )
                else intervention.channel
            ),

            "message": intervention.message,

            "executed_at": (
                intervention.executed_at
            ),

            "result": intervention.result,

            "recovered_amount": (
                intervention.recovered_amount
            ),
        }
        for intervention in interventions
    ]


# ============================================================
# RESET DEMO
# ============================================================

@router.post("/demo/reset")
def reset_demo(
    db: Session = Depends(get_db),
):
    """
    Reset the demo by removing existing cases and
    recreating the original six recovery scenarios.
    """

    # Delete intervention history first
    db.query(
        Intervention
    ).delete(
        synchronize_session=False
    )

    # Delete existing recovery cases
    db.query(
        RecoveryCase
    ).delete(
        synchronize_session=False
    )

    db.commit()

    # ========================================================
    # ORIGINAL DEMO CASES
    # ========================================================

    demo_cases = [
        {
            "customer_id": "customer-004",
            "source": "overdue_invoice",
            "amount": 12000,
            "context": {
                "event_type": "invoice.overdue",
                "failure_reason": (
                    "OVERDUE_RECEIVABLE"
                ),
            },
        },

        {
            "customer_id": "customer-003",
            "source": "subscription_failure",
            "amount": 3000,
            "context": {
                "event_type": (
                    "subscription.halted"
                ),
                "failure_reason": (
                    "RECURRING_MANDATE_DECLINED"
                ),
            },
        },

        {
            "customer_id": "customer-002",
            "source": "checkout_abandonment",
            "amount": 7500,
            "context": {
                "event_type": (
                    "checkout.abandoned"
                ),
                "failure_reason": (
                    "CART_ABANDONMENT"
                ),
            },
        },

        {
            "customer_id": "customer-001",
            "source": "payment_failure",
            "amount": 5000,
            "context": {
                "event_type": (
                    "payment.failed"
                ),
                "failure_reason": (
                    "INSUFFICIENT_FUNDS"
                ),
            },
        },

        {
            "customer_id": "customer-001",
            "source": "payment_failure",
            "amount": 5000,
            "context": {
                "event_type": (
                    "payment.failed"
                ),
                "failure_reason": (
                    "INSUFFICIENT_FUNDS"
                ),
            },
        },

        {
            "customer_id": "customer-001",
            "source": "payment_failure",
            "amount": 5000,
            "context": {
                "event_type": (
                    "payment.failed"
                ),
                "failure_reason": (
                    "INSUFFICIENT_FUNDS"
                ),
            },
        },
    ]

    from app.services.recovery_service import (
        create_case,
    )

    created = []

    for item in demo_cases:
        case, _ = create_case(
            db=db,
            customer_id=item[
                "customer_id"
            ],
            source=item[
                "source"
            ],
            amount=item[
                "amount"
            ],
            context=item[
                "context"
            ],
        )

        created.append(
            serialize_case(case)
        )

    return {
        "success": True,
        "message": (
            "Demo data reset successfully"
        ),
        "cases": created,
    }

@router.post("/autonomous/{case_id}")
def autonomous_recovery(
    case_id: str,
    db: Session = Depends(get_db),
):
    case = db.get(
        RecoveryCase,
        case_id,
    )

    if not case:
        raise HTTPException(
            404,
            "Recovery case not found",
        )

    # --------------------------------
    # STEP 1 — ANALYZE
    # --------------------------------

    analysis = {
        "risk_score": case.risk_score,
        "root_cause": (
            case.root_cause.value
            if hasattr(
                case.root_cause,
                "value",
            )
            else case.root_cause
        ),
        "suggested_action": case.suggested_action,
    }

    # --------------------------------
    # STEP 2 + 3 — EXECUTE
    # --------------------------------

    execution_result = execute_case(
        db,
        case,
    )

    # --------------------------------
    # STEP 4 — EVALUATE
    # --------------------------------

    outcome = analyze_outcome(
        case,
        execution_result,
    )

    # --------------------------------
    # STEP 5 — NEXT ACTION
    # --------------------------------

    return {
        "success": True,

        "case_id": case.id,

        "agent": {
            "status": "completed",
            "mode": "autonomous",
        },

        "analysis": analysis,

        "execution": execution_result,

        "outcome": outcome,

        "next_action": outcome[
            "next_action"
        ],
    }
    # ------------------------------------------------------------
    # Successful recovery
    # ------------------------------------------------------------

    if result["agent_status"] == "RECOVERED":

        intervention = Intervention(
            recovery_case_id=case.id,
            type=result["action"],
            channel=result["channel"].upper(),
            message=(
                "Autonomous recovery agent "
                f"executed action for case #{case.id}"
            ),
            executed_at=datetime.utcnow(),
            result="SUCCESS",
            recovered_amount=float(
                result["recovered_amount"]
            ),
        )

        db.add(intervention)

        case.status = (
            RecoveryCaseStatus.RECOVERED
        )

        db.commit()
        db.refresh(intervention)

    # ------------------------------------------------------------
    # Failed / escalated
    # ------------------------------------------------------------

    elif result["agent_status"] == "ESCALATED":

        if result.get("action") != "manual_review":

            intervention = Intervention(
                recovery_case_id=case.id,
                type=result["action"],
                channel=result["channel"].upper(),
                message=(
                    "Autonomous recovery attempt "
                    f"for case #{case.id}"
                ),
                executed_at=datetime.utcnow(),
                result="FAILED",
                recovered_amount=0.0,
            )

            db.add(intervention)

        case.status = (
            RecoveryCaseStatus.FAILED
        )

        db.commit()

    return {
        **result,

        "case_id":
            case.id,

        "case_status":
            case.status.value,
    }

@router.post("/autonomous/{case_id}")
def autonomous_recovery(
    case_id: str,
    db: Session = Depends(get_db),
):
    """
    Run the autonomous recovery agent.

    Flow:
    1. Analyze the case
    2. Select intervention
    3. Execute intervention
    4. Evaluate outcome
    5. Recommend next action
    """

    # Clean case ID coming from Swagger/UI
    case_id = str(case_id).strip().lstrip("#")

    case = db.get(
        RecoveryCase,
        case_id,
    )

    if not case:
        raise HTTPException(
            status_code=404,
            detail=f"Recovery case not found: {case_id}",
        )

    current_status = (
        case.status.value
        if hasattr(case.status, "value")
        else str(case.status)
    )

    current_status = current_status.lower()

    if current_status != "open":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Case is not open. "
                f"Current status: {current_status}"
            ),
        )

    return autonomous_recovery_agent(
        db=db,
        case=case,
    )