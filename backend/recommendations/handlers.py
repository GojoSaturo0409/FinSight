from abc import ABC, abstractmethod
from typing import Dict, Any, List


class RecommendationHandler(ABC):
    def __init__(self):
        self._next_handler = None

    def set_next(self, handler: 'RecommendationHandler') -> 'RecommendationHandler':
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, user_context: Dict[str, Any], recommendations: List[str]) -> List[str]:
        if self._next_handler:
            return self._next_handler.handle(user_context, recommendations)
        return recommendations


class HighSpendDetector(RecommendationHandler):
    """
    Flags any spending category exceeding 30% of income (per proposal spec),
    and warns if total spending exceeds 80% of income.
    """
    def handle(self, user_context: Dict[str, Any], recommendations: List[str]) -> List[str]:
        income = user_context.get("monthly_income", 1)
        spend = user_context.get("monthly_spend", 0)
        categories = user_context.get("categories", {})

        # Overall spending check
        if income > 0 and spend / income > 0.8:
            pct = round((spend / income) * 100, 1)
            recommendations.append(
                f"High Spend Warning: You are spending {pct}% of your income. "
                f"Consider reducing discretionary spending to stay under 80%."
            )

        # Per-category check: flag any category exceeding 30% of income
        for category, amount in categories.items():
            if income > 0 and amount / income > 0.30:
                cat_pct = round((amount / income) * 100, 1)
                recommendations.append(
                    f"Category Alert: '{category}' is {cat_pct}% of your income (${amount:.0f}/${income:.0f}). "
                    f"The recommended limit per category is 30%."
                )

        if self._next_handler:
            return self._next_handler.handle(user_context, recommendations)
        return recommendations


class SubscriptionAuditHandler(RecommendationHandler):
    """
    Detects recurring subscription charges. Flags if subscriptions exceed 5% of income
    or the absolute total exceeds $50.
    """
    def handle(self, user_context: Dict[str, Any], recommendations: List[str]) -> List[str]:
        income = user_context.get("monthly_income", 1)
        categories = user_context.get("categories", {})
        subs_total = categories.get("Subscriptions", 0)

        recurring_merchants = user_context.get("recurring_merchants", [])

        if subs_total > 50:
            recommendations.append(
                f"Subscription Audit: You've spent ${subs_total:.2f} on subscriptions this month. "
                f"Review and cancel redundant services to save money."
            )

        if income > 0 and subs_total / income > 0.05:
            pct = round((subs_total / income) * 100, 1)
            recommendations.append(
                f"Subscription Warning: Subscriptions are {pct}% of your income. "
                f"Aim to keep recurring charges under 5%."
            )

        if recurring_merchants:
            merchants_list = ", ".join(recurring_merchants[:5])
            recommendations.append(
                f"Recurring Charges Detected: {merchants_list}. "
                f"Check if all of these are still needed."
            )

        if self._next_handler:
            return self._next_handler.handle(user_context, recommendations)
        return recommendations


class SavingsGoalAdvisor(RecommendationHandler):
    """
    Compares actual savings (income - spend) against the user's savings target.
    Provides percentage-based feedback and actionable suggestions.
    """
    def handle(self, user_context: Dict[str, Any], recommendations: List[str]) -> List[str]:
        income = user_context.get("monthly_income", 0)
        spend = user_context.get("monthly_spend", 0)
        savings = income - spend
        target = user_context.get("savings_target", 0)

        if target > 0:
            progress_pct = round((savings / target) * 100, 1) if target > 0 else 0

            if savings >= target:
                overshoot = savings - target
                recommendations.append(
                    f"Great job! You hit your monthly savings target of ${target:.0f} "
                    f"with ${savings:.0f} saved ({progress_pct}%). "
                    f"You have an extra ${overshoot:.0f} this month."
                )
            else:
                shortfall = target - savings
                recommendations.append(
                    f"Goal Check: You are ${shortfall:.0f} short of your ${target:.0f} savings target "
                    f"({progress_pct}% achieved). Consider cutting discretionary spending in your "
                    f"highest category to close the gap."
                )

        if self._next_handler:
            return self._next_handler.handle(user_context, recommendations)
        return recommendations


class InvestmentOpportunityHandler(RecommendationHandler):
    """
    Suggests low-risk investment instruments when a monthly surplus exists.
    Fetches real cached market data from Alpha Vantage via AlphaVantageService.
    """
    def handle(self, user_context: Dict[str, Any], recommendations: List[str]) -> List[str]:
        income = user_context.get("monthly_income", 0)
        spend = user_context.get("monthly_spend", 0)
        surplus = income - spend
        db = user_context.get("_db_session", None)

        if surplus > 500:
            # Try fetching real market data from cache
            market_info = self._get_market_data(db)
            recommendations.append(
                f"Investment Opportunity: You have a surplus of ${surplus:.0f}. "
                f"Consider investing in low-risk index funds. {market_info}"
            )
        elif surplus > 100:
            recommendations.append(
                f"Savings Tip: Your ${surplus:.0f} surplus could grow in a high-yield savings account "
                f"while you build up to a larger investment amount."
            )

        if self._next_handler:
            return self._next_handler.handle(user_context, recommendations)
        return recommendations

    def _get_market_data(self, db) -> str:
        """Fetch cached market data from Alpha Vantage. Falls back to static data if unavailable."""
        if db is None:
            return self._get_static_market_data()

        try:
            from investments.alpha_vantage_service import AlphaVantageService, DEFAULT_SYMBOLS
            portfolio = AlphaVantageService.get_portfolio_summary(DEFAULT_SYMBOLS, db)

            lines = []
            for item in portfolio:
                symbol = item["symbol"]
                price = item["price"]
                trend = item["trend"]
                arrow = "↑" if trend == "up" else "↓" if trend == "down" else "→"
                stale_tag = " (cached)" if item.get("stale") else ""
                lines.append(f"{symbol}: ${price:.2f} {arrow}{stale_tag}")

            return "Market snapshot: " + " | ".join(lines)
        except Exception:
            return self._get_static_market_data()

    @staticmethod
    def _get_static_market_data() -> str:
        """Fallback static market data when DB is unavailable."""
        return "Market snapshot: SPY: $523.40 ↑ | BND: $72.85 ↑ | VTI: $261.20 ↑"
