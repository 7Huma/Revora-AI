from typing import Any

from app.agents.intervention_agent import recommend
from app.agents.risk_detector import calculate_risk
from app.agents.root_cause_agent import diagnose


def analyze_case(
    source: str,
    amount: float,
    context: dict[str, Any] | None = None,
) -> dict:
    """
    Run the complete revenue-recovery decision pipeline.

    Steps:
        1. Calculate financial/recovery risk.
        2. Diagnose the root cause.
        3. Recommend an intervention.
        4. Return a normalized recovery decision.
    """

    if amount < 0:
        raise ValueError("amount cannot be negative")

    context = context or {}

    risk = calculate_risk(
        source,
        amount,
        context,
    )

    root = diagnose(
        source,
        context,
    )

    action = recommend(
        source,
        root,
        risk,
        context,
    )

    return {
        "risk_score": risk["score"],
        "root_cause": root["cause"],
        "recommended_action": action["action"],
        "channel": action["channel"],
        "priority": action["priority"],
        "reason": action["reason"],
    }