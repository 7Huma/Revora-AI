from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.db.models import (
    RecoveryCase,
    RecoveryCaseStatus,
    Intervention,
)

router = APIRouter()


@router.get("/summary")
def summary(db: Session = Depends(get_db)):

    # ============================================================
    # REVENUE AT RISK
    # ============================================================

    at_risk = (
        db.query(
            func.coalesce(
                func.sum(RecoveryCase.amount_at_risk),
                0,
            )
        )
        .scalar()
        or 0
    )

    # ============================================================
    # RECOVERED REVENUE
    #
    # Calculate recovery per CASE and cap it at the amount
    # originally at risk.
    #
    # This prevents duplicate historical interventions from
    # making recovered revenue larger than the revenue exposure.
    # ============================================================

    cases = (
        db.query(RecoveryCase)
        .all()
    )

    recovered = 0.0

    for case in cases:

        case_recovered = (
            db.query(
                func.coalesce(
                    func.sum(
                        Intervention.recovered_amount
                    ),
                    0,
                )
            )
            .filter(
                Intervention.recovery_case_id
                == case.id
            )
            .filter(
                Intervention.result == "SUCCESS"
            )
            .scalar()
            or 0
        )

        # Never allow a case to contribute more recovered
        # revenue than its original amount at risk.
        case_recovered = min(
            float(case_recovered),
            float(case.amount_at_risk or 0),
        )

        recovered += case_recovered

    # ============================================================
    # EXPECTED RECOVERY
    #
    # Expected recovery = amount at risk × recovery probability
    # ============================================================

    expected_recovery = 0.0

    for case in cases:

        amount = float(
            case.amount_at_risk or 0
        )

        risk = float(
            case.risk_score or 0
        )

        source = str(
            case.source or ""
        ).lower()

        base_probability = {
            "payment_failure": 0.82,
            "checkout_abandonment": 0.58,
            "subscription_failure": 0.74,
            "overdue_invoice": 0.68,
            "mandate_retry": 0.78,
        }.get(
            source,
            0.50,
        )

        risk_adjustment = (
            70 - risk
        ) * 0.002

        probability = max(
            0.05,
            min(
                0.95,
                base_probability
                + risk_adjustment,
            ),
        )

        probability = round(
            probability,
            2,
        )

        expected_recovery += (
            amount * probability
        )

    # ============================================================
    # ACTIVE CASES
    # ============================================================

    active = (
        db.query(RecoveryCase)
        .filter(
            RecoveryCase.status.in_(
                [
                    RecoveryCaseStatus.OPEN,
                    RecoveryCaseStatus.IN_PROGRESS,
                ]
            )
        )
        .count()
    )

    # ============================================================
    # RECOVERY RATE
    # ============================================================

    rate = (
        recovered / at_risk * 100
        if at_risk
        else 0
    )

    # ============================================================
    # RESPONSE
    # ============================================================

    return {
        "revenue_at_risk": round(
            float(at_risk),
            2,
        ),

        "recovered_revenue": round(
            recovered,
            2,
        ),

        "expected_recovery": round(
            expected_recovery,
            2,
        ),

        "recovery_rate": round(
            rate,
            2,
        ),

        "active_cases": active,
    }


@router.get("/revenue-at-risk")
def revenue_at_risk(
    db: Session = Depends(get_db),
):

    rows = (
        db.query(RecoveryCase)
        .all()
    )

    return [
        {
            "id": r.id,
            "source": r.source,
            "amount": r.amount_at_risk,
            "risk_score": r.risk_score,
        }
        for r in rows
    ]


@router.get("/recovered-revenue")
def recovered_revenue(
    db: Session = Depends(get_db),
):

    rows = (
        db.query(Intervention)
        .filter(
            Intervention.result == "SUCCESS"
        )
        .all()
    )

    return [
        {
            "id": r.id,
            "case_id": r.recovery_case_id,
            "recovered_amount": r.recovered_amount,
            "result": r.result,
        }
        for r in rows
    ]