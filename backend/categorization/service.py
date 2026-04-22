import os
import logging
from .strategies import CategorizationStrategy, RuleBasedStrategy, MLStrategy
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class CategorizationService:
    """
    Service that delegates transaction categorization to a pluggable Strategy.
    The active strategy can be swapped at runtime via set_strategy() or
    selected at startup via the CATEGORIZATION_STRATEGY environment variable.
    """

    def __init__(self, strategy: CategorizationStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: CategorizationStrategy):
        """Swap the active categorization algorithm at runtime."""
        logger.info("CategorizationService: Strategy switched to %s", type(strategy).__name__)
        self._strategy = strategy

    @property
    def current_strategy_name(self) -> str:
        return type(self._strategy).__name__

    def categorize_single(self, transaction: Dict[str, Any]) -> str:
        """Categorize a single transaction."""
        return self._strategy.categorize(transaction)

    def process_transactions(self, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Categorize uncategorized or unknown transactions in batch.
        Already-categorized transactions are left unchanged.
        """
        for tx in transactions:
            current_cat = tx.get("category", "")
            if not current_cat or current_cat in ("Unknown", "Uncategorized"):
                tx["category"] = self._strategy.categorize(tx)
        return transactions


def get_default_service() -> CategorizationService:
    """
    Factory function that reads CATEGORIZATION_STRATEGY env var
    and returns a CategorizationService with the appropriate strategy.

    Values: 'rule' (default) or 'ml'
    """
    strategy_name = os.getenv("CATEGORIZATION_STRATEGY", "rule").lower()

    if strategy_name == "ml":
        logger.info("Config: Using MLStrategy for categorization")
        strategy = MLStrategy()
    else:
        logger.info("Config: Using RuleBasedStrategy for categorization")
        strategy = RuleBasedStrategy()

    return CategorizationService(strategy=strategy)
