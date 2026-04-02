from .handlers import HighSpendDetector, SubscriptionAuditHandler, SavingsGoalAdvisor, InvestmentOpportunityHandler
from typing import Dict, Any, List

class RecommendationChain:
    def __init__(self):
        self.entry_handler = HighSpendDetector()
        subs = SubscriptionAuditHandler()
        goals = SavingsGoalAdvisor()
        investments = InvestmentOpportunityHandler()

        # Connect chain
        self.entry_handler.set_next(subs).set_next(goals).set_next(investments)

    def get_recommendations(self, user_context: Dict[str, Any]) -> List[str]:
        recommendations: List[str] = []
        return self.entry_handler.handle(user_context, recommendations)
