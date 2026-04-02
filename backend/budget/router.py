from fastapi import APIRouter
from typing import List, Dict, Any
from .monitor import BudgetMonitor
from .observers import EmailNotifier, InAppNotifier, LoggingObserver

router = APIRouter()

# Instantiate global mock monitor for route
budget_monitor = BudgetMonitor()
budget_monitor.attach(EmailNotifier())
budget_monitor.attach(InAppNotifier())
budget_monitor.attach(LoggingObserver())

@router.post("/evaluate")
def evaluate_budget(transactions: List[Dict[str, Any]], budgets: Dict[str, float]):
    budget_monitor.evaluate(transactions, budgets)
    return {"status": "success", "message": "Budget evaluated. Alerts fired if any thresholds were crossed."}
