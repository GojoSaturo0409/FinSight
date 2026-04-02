from .strategies import CategorizationStrategy, RuleBasedStrategy, MLStrategy
from typing import Dict, Any, List

class CategorizationService:
    def __init__(self, strategy: CategorizationStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: CategorizationStrategy):
        self._strategy = strategy

    def process_transactions(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        for tx in transactions:
            if tx.get("category") == "Unknown" or tx.get("category") == "Uncategorized" or not tx.get("category"):
                tx["category"] = self._strategy.categorize(tx)
        return transactions
