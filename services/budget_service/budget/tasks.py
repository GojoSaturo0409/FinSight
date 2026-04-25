from celery import Celery
import os
import smtplib
from email.message import EmailMessage

celery_app = Celery("budget_tasks", broker=os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//"))

@celery_app.task(name="budget.tasks.send_email_alert")
def send_email_alert(category, threshold, current_spend, alert_level):
    """
    Sends an email asynchronously via MailJet REST API.
    Falls back gracefully if keys are omitted.
    """
    api_key = os.environ.get('MAILJET_API_KEY')
    api_secret = os.environ.get('MAILJET_SECRET_KEY')
    sender_email = os.environ.get('MAILJET_SENDER_EMAIL', 'noreply@finsight.app')
    recipient_email = os.environ.get('MAILJET_RECIPIENT_EMAIL', 'test@example.com')

    if not api_key or not api_secret:
        print(f"CELERY TASK MOCKED: EMAIL ALERT -> {category} has {alert_level} its threshold of {threshold}. Keys missing.")
        return True

    from mailjet_rest import Client
    mailjet = Client(auth=(api_key, api_secret), version='v3.1')
    data = {
      'Messages': [
        {
          "From": { "Email": sender_email, "Name": "FinSight Notifications" },
          "To": [{ "Email": recipient_email }],
          "Subject": f"FinSight Budget Alert: {category} {alert_level.upper()}",
          "TextPart": f"Your spending in '{category}' is ${current_spend:.2f}, triggering a {alert_level} alert (limit: ${threshold:.2f}).",
        }
      ]
    }
    
    try:
        result = mailjet.send.create(data=data)
        print(f"MAILJET SUCCESS: {result.status_code}")
    except Exception as e:
        print(f"MAILJET ERROR: {e}")

    return True

@celery_app.task(name="budget.tasks.send_push_notification")
def send_push_notification(category, threshold, current_spend, alert_level):
    """
    Sends a push notification asynchronously via Firebase Cloud Messaging.
    Falls back gracefully if credentials are not configured.
    """
    server_key = os.environ.get("FIREBASE_SERVER_KEY")
    try:
        import firebase_admin
        from firebase_admin import credentials, messaging

        if not firebase_admin._apps:
             # Just instantiate default app if a service account path is provided
             cert_path = os.environ.get("FIREBASE_CERT_PATH")
             if cert_path and os.path.exists(cert_path):
                 cred = credentials.Certificate(cert_path)
                 firebase_admin.initialize_app(cred)
             else:
                 print(f"CELERY TASK MOCKED: PUSH ALERT -> Budget alert for {category}. Credentials missing.")
                 return True

        message = messaging.Message(
            notification=messaging.Notification(
                title=f"Budget {alert_level.upper()}: {category}",
                body=f"You've spent ${current_spend:.2f} in {category} (limit: ${threshold:.2f})"
            ),
            topic='budget_alerts'
        )
        response = messaging.send(message)
        print(f"FIREBASE SUCCESS: {response}")
    except Exception as e:
        print(f"FIREBASE ERROR/MOCKED: {e}")
        
    return True
