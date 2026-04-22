from fastapi import APIRouter
from typing import List, Dict, Any
from pydantic import BaseModel
from .monitor import BudgetMonitor
from .observers import EmailNotifier, InAppNotifier, LoggingObserver

router = APIRouter()

# Instantiate global budget monitor with all three observers
budget_monitor = BudgetMonitor()
budget_monitor.attach(EmailNotifier())
budget_monitor.attach(InAppNotifier())
budget_monitor.attach(LoggingObserver())

# In-memory alert history for the GET endpoint
_alert_history: List[Dict[str, Any]] = []


class BudgetEvaluationRequest(BaseModel):
    transactions: List[Dict[str, Any]]
    budgets: Dict[str, float]


@router.post("/evaluate")
def evaluate_budget(request: BudgetEvaluationRequest):
    """
    Evaluate spending against budgets and fire alerts.
    Returns a list of triggered alerts with delivery status.
    """
    alerts = budget_monitor.evaluate(request.transactions, request.budgets)

    # Store in history
    _alert_history.extend(alerts)

    return {
        "status": "success",
        "alerts_triggered": len(alerts),
        "alerts": alerts,
        "message": (
            f"{len(alerts)} alert(s) fired across all channels."
            if alerts
            else "All spending within budget. No alerts triggered."
        ),
    }


@router.get("/alerts")
def get_recent_alerts(limit: int = 20):
    """Return recent budget alerts from in-memory history."""
    recent = _alert_history[-limit:] if _alert_history else []
    return {
        "status": "success",
        "count": len(recent),
        "alerts": list(reversed(recent)),  # newest first
    }
