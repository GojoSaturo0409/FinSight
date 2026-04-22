from typing import List, Dict, Any
from .observers import AlertObserver
import logging

logger = logging.getLogger(__name__)


class BudgetMonitor:
    """
    Observer-pattern subject that evaluates spending against budget thresholds
    and notifies all registered observers when limits are breached.
    
    Supports multi-level thresholds:
      - 'warning'  at 80% of budget
      - 'exceeded' at 100% of budget
      - 'critical' at 120% of budget
    """

    # Threshold levels as (ratio, label)
    THRESHOLD_LEVELS = [
        (0.80, "warning"),
        (1.00, "exceeded"),
        (1.20, "critical"),
    ]

    def __init__(self):
        self._observers: List[AlertObserver] = []

    def attach(self, observer: AlertObserver) -> None:
        """Register a new observer for budget alerts."""
        if observer not in self._observers:
            self._observers.append(observer)
            logger.info("BudgetMonitor: Attached observer %s", type(observer).__name__)

    def detach(self, observer: AlertObserver) -> None:
        """Remove an observer from budget alerts."""
        self._observers.remove(observer)
        logger.info("BudgetMonitor: Detached observer %s", type(observer).__name__)

    def notify(self, category: str, threshold: float, current_spend: float,
               alert_level: str = "exceeded") -> List[Dict[str, Any]]:
        """Notify all observers about a budget alert and collect delivery statuses."""
        results = []
        for observer in self._observers:
            result = observer.update(category, threshold, current_spend, alert_level)
            if result:
                results.append(result)
        return results

    # Alias per the proposal spec
    notify_all = notify

    def evaluate(self, transactions: List[Dict[str, Any]],
                 budgets: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Evaluate current spending against budgets and fire multi-level alerts.

        Args:
            transactions: List of transaction dicts with 'category' and 'amount' keys
            budgets: Dict mapping category -> budget limit (e.g. {"Food": 500})

        Returns:
            List of triggered alert records with details
        """
        # Aggregate spending by category
        category_spend: Dict[str, float] = {}
        for tx in transactions:
            category = tx.get("category", "Unknown")
            category_spend[category] = category_spend.get(category, 0) + tx.get("amount", 0)

        triggered_alerts: List[Dict[str, Any]] = []

        for category, spend in category_spend.items():
            limit = budgets.get(category)
            if not limit:
                continue

            ratio = spend / limit

            # Fire alerts for each threshold level that is breached
            for threshold_ratio, level in self.THRESHOLD_LEVELS:
                if ratio >= threshold_ratio:
                    delivery_results = self.notify(category, limit, spend, level)
                    triggered_alerts.append({
                        "category": category,
                        "alert_level": level,
                        "spend": round(spend, 2),
                        "limit": round(limit, 2),
                        "ratio": round(ratio, 2),
                        "delivery": delivery_results,
                    })

        if triggered_alerts:
            logger.info("BudgetMonitor: %d alert(s) triggered", len(triggered_alerts))
        else:
            logger.info("BudgetMonitor: All spending within budget")

        return triggered_alerts
