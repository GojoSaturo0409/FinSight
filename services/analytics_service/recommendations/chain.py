from .handlers import HighSpendDetector, SubscriptionAuditHandler, SavingsGoalAdvisor, InvestmentOpportunityHandler
from typing import Dict, Any, List
from sqlalchemy.orm import Session


class RecommendationChain:
    def __init__(self):
        self.entry_handler = HighSpendDetector()
        subs = SubscriptionAuditHandler()
        goals = SavingsGoalAdvisor()
        investments = InvestmentOpportunityHandler()

        # Connect chain: HighSpend -> Subscriptions -> SavingsGoal -> Investment
        self.entry_handler.set_next(subs).set_next(goals).set_next(investments)

    def get_recommendations(self, user_context: Dict[str, Any], db: Session = None) -> List[str]:
        """
        Run the full recommendation chain.
        Optionally accepts a DB session for Alpha Vantage cache lookups.
        """
        if db is not None:
            user_context["_db_session"] = db

        recommendations: List[str] = []
        return self.entry_handler.handle(user_context, recommendations)
