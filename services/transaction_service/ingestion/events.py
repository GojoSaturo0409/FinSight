import pika
import json
import logging

logger = logging.getLogger(__name__)

def publish_transaction_ingested(tx):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', port=5672))
        channel = connection.channel()
        channel.exchange_declare(exchange='transaction_events', exchange_type='fanout')
        
        tx_data = {
            "id": tx.id,
            "amount": float(tx.amount),
            "currency": tx.currency,
            "category": tx.category,
            "merchant": tx.merchant,
            "date": tx.date.strftime("%Y-%m-%d") if hasattr(tx.date, "strftime") else str(tx.date),
            "source": tx.source,
            "user_id": str(tx.user_id)
        }
        
        channel.basic_publish(
            exchange='transaction_events',
            routing_key='',
            body=json.dumps(tx_data),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        logger.info(f"Published TransactionIngested for {tx.id}")
    except Exception as e:
        logger.error(f"Failed to publish TransactionIngested: {e}")
