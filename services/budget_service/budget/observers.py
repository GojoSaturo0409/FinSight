from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import os
import logging
import datetime

logger = logging.getLogger(__name__)


class AlertObserver(ABC):
    """Abstract base class for budget alert observers (Observer Pattern)."""

    @abstractmethod
    def update(self, category: str, threshold: float, current_spend: float,
               alert_level: str = "exceeded") -> Dict[str, Any]:
        """
        Called when a budget threshold is breached.

        Args:
            category: The spending category (e.g. 'Food', 'Transport')
            threshold: The budget limit for this category
            current_spend: The actual spending amount
            alert_level: One of 'warning' (80%), 'exceeded' (100%), 'critical' (120%)

        Returns:
            Dict with delivery status: {"delivered": bool, "channel": str, "detail": str}
        """
        pass


class EmailNotifier(AlertObserver):
    """
    Sends budget alert emails via the Mailjet v3.1/send REST API.
    Falls back to console logging when API keys are not set (dev mode).
    
    Env vars: MAILJET_API_KEY, MAILJET_SECRET_KEY, MAILJET_SENDER_EMAIL
    """

    def __init__(self):
        self.api_key = os.getenv("MAILJET_API_KEY", "")
        self.secret_key = os.getenv("MAILJET_SECRET_KEY", "")
        self.sender_email = os.getenv("MAILJET_SENDER_EMAIL", "noreply@finsight.app")
        self.recipient_email = os.getenv("MAILJET_RECIPIENT_EMAIL", "user@example.com")

    def update(self, category: str, threshold: float, current_spend: float,
               alert_level: str = "exceeded") -> Dict[str, Any]:

        subject = f"FinSight Budget Alert: {category} {alert_level.upper()}"
        body = (
            f"Your spending in '{category}' has reached ${current_spend:.2f}, "
            f"which is {alert_level} your budget of ${threshold:.2f}.\n\n"
            f"Alert Level: {alert_level.upper()}\n"
            f"Overage: ${max(0, current_spend - threshold):.2f}\n\n"
            f"— FinSight Budget Monitor"
        )

        # Fire and forget passing data to our Celery worker via RabbitMQ
        from budget.tasks import send_email_alert
        send_email_alert.delay(category, threshold, current_spend, alert_level)
        return {"delivered": True, "channel": "email", "detail": "Dispatched to Celery worker"}


class InAppNotifier(AlertObserver):
    """
    Sends push notifications via Firebase Cloud Messaging (FCM) HTTP API.
    Falls back to console logging when API keys are not set (dev mode).
    
    Env var: FIREBASE_SERVER_KEY
    """

    def __init__(self):
        self.server_key = os.getenv("FIREBASE_SERVER_KEY", "")
        self.device_token = os.getenv("FIREBASE_DEVICE_TOKEN", "")

    def update(self, category: str, threshold: float, current_spend: float,
               alert_level: str = "exceeded") -> Dict[str, Any]:

        title = f"Budget {alert_level.upper()}: {category}"
        body = (f"You've spent ${current_spend:.2f} in {category} "
                f"(limit: ${threshold:.2f})")

        # Fire async push notification task via Celery
        from budget.tasks import send_push_notification
        send_push_notification.delay(category, threshold, current_spend, alert_level)
        return {"delivered": True, "channel": "push", "detail": "Dispatched to Celery worker"}


class LoggingObserver(AlertObserver):
    """
    Writes structured audit log entries for all budget threshold breaches.
    Logs to both Python logger and an audit.log file.
    """

    def __init__(self, log_file: str = "audit.log"):
        self._audit_logger = logging.getLogger("finsight.audit")
        if not self._audit_logger.handlers:
            target_log = os.getenv("AUDIT_LOG_FILE", log_file)
            try:
                log_dir = os.path.dirname(target_log)
                if log_dir:
                    os.makedirs(log_dir, exist_ok=True)
                handler = logging.FileHandler(target_log)
            except PermissionError:
                fallback_log = "/tmp/finsight_audit.log"
                handler = logging.FileHandler(fallback_log)
                logger.warning(
                    "No permission for audit log '%s'; using fallback '%s'",
                    target_log,
                    fallback_log,
                )

            handler.setFormatter(logging.Formatter(
                "%(asctime)s | BUDGET_ALERT | %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            ))
            self._audit_logger.addHandler(handler)
            self._audit_logger.setLevel(logging.INFO)

    def update(self, category: str, threshold: float, current_spend: float,
               alert_level: str = "exceeded") -> Dict[str, Any]:

        log_entry = (
            f"level={alert_level} | category={category} | "
            f"spend={current_spend:.2f} | limit={threshold:.2f} | "
            f"overage={max(0, current_spend - threshold):.2f}"
        )
        self._audit_logger.info(log_entry)
        print(f"📝 [LoggingObserver] AUDIT: {log_entry}")

        return {"delivered": True, "channel": "audit_log", "detail": log_entry}
