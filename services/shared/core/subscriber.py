import pika
import json
import logging
import traceback
import time
from shared.database import SessionLocal
from categorization.service import get_default_service
from budget.monitor import BudgetMonitor

logger = logging.getLogger(__name__)

# Singletons
categorization_service = get_default_service()
budget_monitor = BudgetMonitor()

def process_transaction(tx_data):
    import shared.models
    db = SessionLocal()
    try:
        cat_txs = categorization_service.process_transactions([tx_data])
        updated_category = cat_txs[0]["category"]
        
        db_tx = db.query(models.Transaction).filter_by(id=tx_data["id"]).first()
        if db_tx and db_tx.category == "Uncategorized" and updated_category != "Uncategorized":
            db_tx.category = updated_category
            db.commit()

        user_id = db_tx.user_id if db_tx else tx_data.get("user_id")
        if user_id:
            budgets = db.query(models.Budget).filter_by(user_id=user_id).all()
            budget_dict = {b.category: float(b.limit_amount) for b in budgets}
            
            all_txs = db.query(models.Transaction).filter_by(user_id=user_id).all()
            tx_list = [{"category": t.category, "amount": float(t.amount)} for t in all_txs]
            
            budget_monitor.evaluate(tx_list, budget_dict)
            logger.info(f"Processed TransactionIngested event {tx_data['id']} and evaluated budgets.")

    except Exception as e:
        logger.error(f"Error processing transaction in Core: {e}")
        db.rollback()
    finally:
        db.close()

def callback(ch, method, properties, body):
    try:
        tx_data = json.loads(body)
        logger.info(f"Core Subscriber received TransactionIngested: {tx_data['id']}")
        process_transaction(tx_data)
    except Exception as e:
        logger.error(f"Core Subscriber error: {e}")
        traceback.print_exc()

def start_core_subscriber():
    """Background worker loop to listen for RabbitMQ events."""
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq', port=5672))
            channel = connection.channel()
            channel.exchange_declare(exchange='transaction_events', exchange_type='fanout')
            
            result = channel.queue_declare(queue='', exclusive=True)
            queue_name = result.method.queue
            
            channel.queue_bind(exchange='transaction_events', queue=queue_name)
            
            channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
            
            logger.info("Core Subscriber listening for TransactionIngested events...")
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            logger.warning("RabbitMQ not ready. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Core Subscriber connection error: {e}")
            time.sleep(5)
