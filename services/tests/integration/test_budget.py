import pytest
import pika
import json
import time
from services.budget_service.budget.monitor import BudgetMonitor

def test_budget_monitor_threshold_evaluation():
    # Simulated input
    transactions = [
        {"category": "Food", "amount": 80.0},
        {"category": "Transport", "amount": 20.0}
    ]
    budgets = {"Food": 50.0, "Transport": 100.0}

    monitor = BudgetMonitor()
    alerts = monitor.evaluate(transactions, budgets)

    # Food limit is 50. Spend is 80. Ratio is 160%.
    # This should trigger warning(0.8), exceeded(1.0), and critical(1.2)!
    assert len(alerts) > 0

    food_alerts = [a for a in alerts if a["category"] == "Food"]
    assert len(food_alerts) == 3, "Should trigger all three alert levels for Food"
    
    levels = [a["alert_level"] for a in food_alerts]
    assert "warning" in levels
    assert "exceeded" in levels
    assert "critical" in levels

def test_budget_pub_sub_dispatch():
    # Test if message actually reaches RabbitMQ and is readable
    monitor = BudgetMonitor()
    
    # 1. Purge/setup queue
    import os
    rmq_host = os.getenv("RABBITMQ_HOST", "localhost")
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rmq_host, port=5672))
    channel = connection.channel()
    channel.exchange_declare(exchange='budget_events', exchange_type='fanout')
    
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='budget_events', queue=queue_name)

    # 2. Fire the monitor publisher
    delivery = monitor.notify("Entertainment", 100.0, 150.0, "exceeded")
    
    # Verify the monitor claims success
    assert delivery[0]["delivered"] is True
    assert delivery[0]["channel"] == "rabbitmq"

    # 3. Read it back identically to how subscriber.py does it!
    method, properties, body = channel.basic_get(queue=queue_name, auto_ack=True)
    assert body is not None, "Message was not published!"
    
    data = json.loads(body)
    assert data["category"] == "Entertainment"
    assert data["threshold"] == 100.0
    assert data["current_spend"] == 150.0
    assert data["alert_level"] == "exceeded"
    
    connection.close()

if __name__ == "__main__":
    pytest.main(["-v", __file__])
