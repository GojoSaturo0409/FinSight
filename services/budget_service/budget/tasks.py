from celery import Celery
import os
import smtplib
from email.message import EmailMessage

celery_app = Celery("budget_tasks", broker=os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//"))

@celery_app.task(name="budget.tasks.send_email_alert")
def send_email_alert(category, threshold, current_spend, alert_level):
    """
    Simulates sending an email asynchronously via MailJet or SMTP.
    """
    print(f"CELERY TASK EXECUTED: EMAIL ALERT -> {category} has {alert_level} its threshold of {threshold}. Current spend: {current_spend}")
    # return True to mark task successful
    return True

@celery_app.task(name="budget.tasks.send_push_notification")
def send_push_notification(category, threshold, current_spend, alert_level):
    """
    Simulates sending a push notification asynchronously via Firebase.
    """
    print(f"CELERY TASK EXECUTED: PUSH ALERT -> Budget alert for {category}. Current: {current_spend}, Threshold: {threshold}")
    return True
