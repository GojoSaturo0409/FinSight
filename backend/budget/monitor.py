from typing import List, Dict, Any
from .observers import AlertObserver
import logging
import json
import pika

logger = logging.getLogger(__name__)


class BudgetMonitor:
    """
    Observer-pattern subject that evaluates spending against budget thresholds
    and notifies all registered observers when limits are breached.
    Now refactored to use RabbitMQ Pub-Sub decoupling.
    """

    # Threshold levels as (ratio, label)
    THRESHOLD_LEVELS = [
        (0.80, "warning"),
        (1.00, "exceeded"),
        (1.20, "critical"),
    ]

    def __init__(self):
        pass

    def attach(self, observer: AlertObserver) -> None:
        pass

    def detach(self, observer: AlertObserver) -> None:
        pass

    def notify(self, category: str, threshold: float, current_spend: float,
               alert_level: str = "exceeded") -> List[Dict[str, Any]]:
        """Publish a budget alert to RabbitMQ."""
        payload = {
            "category": category,
            "threshold": threshold,
            "current_spend": current_spend,
            "alert_level": alert_level
        }
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', port=5672))
            channel = connection.channel()
            channel.exchange_declare(exchange='budget_events', exchange_type='fanout')
            channel.basic_publish(
                exchange='budget_events',
                routing_key='',
                body=json.dumps(payload),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            connection.close()
            logger.info("BudgetMonitor: Published event for %s (%s)", category, alert_level)
            return [{"delivered": True, "channel": "rabbitmq", "detail": "Published to broker"}]
        except BaseException as e:
            logger.error("BudgetMonitor: Failed to publish event: %s", str(e))
            return [{"delivered": False, "channel": "rabbitmq", "detail": str(e)}]

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
