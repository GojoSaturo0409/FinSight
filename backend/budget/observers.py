from abc import ABC, abstractmethod

class AlertObserver(ABC):
    @abstractmethod
    def update(self, category: str, threshold: float, current_spend: float) -> None:
        pass

class EmailNotifier(AlertObserver):
    def update(self, category: str, threshold: float, current_spend: float) -> None:
        # Mocking Mailjet /v3.1/send API
        print(f"📧 [EmailNotifier] Sending email via Mailjet: Budget exceeded for {category}. "
              f"Current spend: {current_spend}, Threshold: {threshold}")

class InAppNotifier(AlertObserver):
    def update(self, category: str, threshold: float, current_spend: float) -> None:
        # Mocking Firebase Cloud Messaging
        print(f"📱 [InAppNotifier] Sending push via Firebase: Alert for {category}! "
              f"You've spent {current_spend} (Limit: {threshold}).")

class LoggingObserver(AlertObserver):
    def update(self, category: str, threshold: float, current_spend: float) -> None:
        # Audit Log
        print(f"📝 [LoggingObserver] AUDIT LOG: Budget Threshold Breach -> "
              f"Category: {category}, Spend: {current_spend}, Limit: {threshold}")
