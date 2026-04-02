from abc import ABC, abstractmethod
from typing import Dict, Any

class CategorizationStrategy(ABC):
    @abstractmethod
    def categorize(self, transaction: Dict[str, Any]) -> str:
        pass

class RuleBasedStrategy(CategorizationStrategy):
    def __init__(self):
        self.rules = {
            "uber": "Transport",
            "lyft": "Transport",
            "mcdonalds": "Food",
            "starbucks": "Food",
            "netflix": "Subscriptions",
            "spotify": "Subscriptions",
            "rent": "Housing",
            "electric": "Utilities"
        }

    def categorize(self, transaction: Dict[str, Any]) -> str:
        merchant = transaction.get("merchant", "").lower()
        for keyword, category in self.rules.items():
            if keyword in merchant:
                return category
        return "Miscellaneous"

class MLStrategy(CategorizationStrategy):
    def __init__(self):
        # In a real scenario, this loads a Naive Bayes or similar ML model.
        pass

    def categorize(self, transaction: Dict[str, Any]) -> str:
        # Dummy mock prediction returning based on simple deterministic logic mimicking ML
        amount = transaction.get("amount", 0)
        merchant = transaction.get("merchant", "").lower()
        
        # Simulating some ML inference logic
        if amount > 1000 and "rent" in merchant:
            return "Housing - ML Predicted"
        elif "amazon" in merchant:
            return "Shopping - ML Predicted"
            
        # fallback to standard Rules
        return RuleBasedStrategy().categorize(transaction)
