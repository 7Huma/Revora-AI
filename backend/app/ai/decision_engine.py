from typing import Any

from app.agents.revenue_agent import analyze_case


class DecisionEngine:
    """
    Entry point for making a revenue-recovery decision.
    """

    def decide(
        self,
        source: str,
        amount: float,
        context: dict[str, Any] | None = None,
    ) -> dict:
        return analyze_case(
            source,
            amount,
            context or {},
        )