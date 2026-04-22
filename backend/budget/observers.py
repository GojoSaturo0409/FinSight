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

        # If Mailjet keys are configured, make real API call
        if self.api_key and self.secret_key:
            try:
                import httpx

                payload = {
                    "Messages": [{
                        "From": {"Email": self.sender_email, "Name": "FinSight"},
                        "To": [{"Email": self.recipient_email}],
                        "Subject": subject,
                        "TextPart": body,
                    }]
                }

                response = httpx.post(
                    "https://api.mailjet.com/v3.1/send",
                    json=payload,
                    auth=(self.api_key, self.secret_key),
                    timeout=10.0,
                )

                if response.status_code == 200:
                    logger.info("📧 EmailNotifier: Mailjet email sent for %s (%s)", category, alert_level)
                    return {"delivered": True, "channel": "email", "detail": "Mailjet API success"}
                else:
                    logger.warning("📧 EmailNotifier: Mailjet returned %d: %s",
                                   response.status_code, response.text)
                    return {"delivered": False, "channel": "email",
                            "detail": f"Mailjet HTTP {response.status_code}"}

            except Exception as e:
                logger.error("📧 EmailNotifier: Mailjet call failed: %s", str(e))
                return {"delivered": False, "channel": "email", "detail": str(e)}
        else:
            # Dev mode fallback — print to console
            print(f"📧 [EmailNotifier] {alert_level.upper()} alert for {category}: "
                  f"Spent ${current_spend:.2f} / Limit ${threshold:.2f}")
            return {"delivered": True, "channel": "email", "detail": "Dev mode (console print)"}


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

        # If Firebase key is configured, make real FCM call
        if self.server_key and self.device_token:
            try:
                import httpx

                payload = {
                    "to": self.device_token,
                    "notification": {
                        "title": title,
                        "body": body,
                    },
                    "data": {
                        "category": category,
                        "alert_level": alert_level,
                        "current_spend": str(current_spend),
                        "threshold": str(threshold),
                    }
                }

                response = httpx.post(
                    "https://fcm.googleapis.com/fcm/send",
                    json=payload,
                    headers={
                        "Authorization": f"key={self.server_key}",
                        "Content-Type": "application/json",
                    },
                    timeout=10.0,
                )

                if response.status_code == 200:
                    logger.info("📱 InAppNotifier: Firebase push sent for %s (%s)", category, alert_level)
                    return {"delivered": True, "channel": "push", "detail": "Firebase FCM success"}
                else:
                    logger.warning("📱 InAppNotifier: Firebase returned %d: %s",
                                   response.status_code, response.text)
                    return {"delivered": False, "channel": "push",
                            "detail": f"Firebase HTTP {response.status_code}"}

            except Exception as e:
                logger.error("📱 InAppNotifier: Firebase call failed: %s", str(e))
                return {"delivered": False, "channel": "push", "detail": str(e)}
        else:
            # Dev mode fallback — print to console
            print(f"📱 [InAppNotifier] {title}: {body}")
            return {"delivered": True, "channel": "push", "detail": "Dev mode (console print)"}


class LoggingObserver(AlertObserver):
    """
    Writes structured audit log entries for all budget threshold breaches.
    Logs to both Python logger and an audit.log file.
    """

    def __init__(self, log_file: str = "audit.log"):
        self._audit_logger = logging.getLogger("finsight.audit")
        if not self._audit_logger.handlers:
            handler = logging.FileHandler(log_file)
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
