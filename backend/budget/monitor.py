from typing import List, Dict, Any
from .observers import AlertObserver

class BudgetMonitor:
    def __init__(self):
        self._observers: List[AlertObserver] = []

    def attach(self, observer: AlertObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: AlertObserver) -> None:
        self._observers.remove(observer)

    def notify(self, category: str, threshold: float, current_spend: float) -> None:
        for observer in self._observers:
            observer.update(category, threshold, current_spend)

    def evaluate(self, transactions: List[Dict[str, Any]], budgets: Dict[str, float]) -> None:
        """
        Evaluate current spending against budgets.
        `budgets` is a dict of category -> threshold (e.g. {"Food": 500, "Transport": 200})
        """
        category_spend = {}
        for tx in transactions:
            category = tx.get("category", "Unknown")
            category_spend[category] = category_spend.get(category, 0) + tx.get("amount", 0)

        for category, spend in category_spend.items():
            limit = budgets.get(category)
            if limit and spend > limit:
                # Fire alerts to all observers
                self.notify(category, limit, spend)
