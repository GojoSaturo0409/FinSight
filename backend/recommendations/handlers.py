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
    def handle(self, user_context: Dict[str, Any], recommendations: List[str]) -> List[str]:
        income = user_context.get("monthly_income", 1)
        spend = user_context.get("monthly_spend", 0)
        
        # Check standard 30% rule for housing, if applicable, or total spend
        if spend / income > 0.8:
            recommendations.append("High Spend Warning: You are spending over 80% of your income.")
            
        if self._next_handler:
            return self._next_handler.handle(user_context, recommendations)
        return recommendations

class SubscriptionAuditHandler(RecommendationHandler):
    def handle(self, user_context: Dict[str, Any], recommendations: List[str]) -> List[str]:
        # Assume user_context contains categorized totals
        subs_total = user_context.get("categories", {}).get("Subscriptions", 0)
        if subs_total > 50:
            recommendations.append("Action: You've spent over $50 on subscriptions this month. Review and cancel redundant services.")
            
        if self._next_handler:
            return self._next_handler.handle(user_context, recommendations)
        return recommendations

class SavingsGoalAdvisor(RecommendationHandler):
    def handle(self, user_context: Dict[str, Any], recommendations: List[str]) -> List[str]:
        income = user_context.get("monthly_income", 0)
        spend = user_context.get("monthly_spend", 0)
        savings = income - spend
        
        target = user_context.get("savings_target", 0)
        if target > 0 and savings < target:
            recommendations.append(f"Goal Check: You are short of your monthly savings target by {target - savings}.")
        elif savings >= target > 0:
            recommendations.append("Great job! You hit your monthly savings target.")
            
        if self._next_handler:
            return self._next_handler.handle(user_context, recommendations)
        return recommendations

class InvestmentOpportunityHandler(RecommendationHandler):
    def handle(self, user_context: Dict[str, Any], recommendations: List[str]) -> List[str]:
        income = user_context.get("monthly_income", 0)
        spend = user_context.get("monthly_spend", 0)
        surplus = income - spend
        
        if surplus > 500:
            # Mock Alpha Vantage Data Call
            av_data = {"SPY": "Up 1.2%", "Bonds": "Stable 4.5% yield"}
            recommendations.append(f"Opportunity: You have a surplus of {surplus}. "
                                   f"Consider low-risk index funds. Market trend today: {av_data['SPY']}.")
            
        if self._next_handler:
            return self._next_handler.handle(user_context, recommendations)
        return recommendations
