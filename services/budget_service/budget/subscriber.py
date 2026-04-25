import pika
import traceback
import json
import logging
import time
from .observers import EmailNotifier, InAppNotifier, LoggingObserver

logger = logging.getLogger(__name__)

# Singletons for our observers
observers = [
    EmailNotifier(),
    InAppNotifier(),
    LoggingObserver(log_file="audit.log")
]

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        logger.info(f"Subscriber received budget event: {data}")
        category = data["category"]
        threshold = data["threshold"]
        current_spend = data["current_spend"]
        alert_level = data["alert_level"]
        
        for obs in observers:
            obs.update(category, threshold, current_spend, alert_level)
            
    except Exception as e:
        logger.error(f"Error processing budget event: {e}")
        traceback.print_exc()

def start_subscriber():
    """Background worker loop to listen for RabbitMQ events."""
    while True:
        try:
            import os
            rmq_host = os.getenv("RABBITMQ_HOST", "rabbitmq")
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rmq_host, port=5672))
            channel = connection.channel()
            channel.exchange_declare(exchange='budget_events', exchange_type='fanout')
            
            result = channel.queue_declare(queue='', exclusive=True)
            queue_name = result.method.queue
            
            channel.queue_bind(exchange='budget_events', queue=queue_name)
            
            channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
            
            logger.info("Budget Event Subscriber started. Waiting for messages.")
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            logger.warning("RabbitMQ not ready. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Subscriber error: {e}")
            time.sleep(5)
