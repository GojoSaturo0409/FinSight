from fastapi import APIRouter, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .monitor import BudgetMonitor
from .observers import EmailNotifier, InAppNotifier, LoggingObserver
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import get_db
import models

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


class BudgetLimitRequest(BaseModel):
    category: str
    limit_amount: float


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


@router.post("/evaluate-auto")
def evaluate_budget_auto(db: Session = Depends(get_db)):
    """
    Auto-evaluate: pulls transactions and budgets from DB, then runs the monitor.
    """
    # Get all transactions
    txs = db.query(models.Transaction).all()
    transaction_dicts = [
        {"category": tx.category, "amount": tx.amount}
        for tx in txs
    ]

    # Get all budgets
    budgets_db = db.query(models.Budget).all()
    budgets = {b.category: b.limit_amount for b in budgets_db}

    if not budgets:
        return {"status": "success", "alerts_triggered": 0, "alerts": [],
                "message": "No budgets configured."}

    alerts = budget_monitor.evaluate(transaction_dicts, budgets)
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


@router.get("/limits")
def get_budget_limits(db: Session = Depends(get_db)):
    """Get all budget limits from DB."""
    budgets = db.query(models.Budget).all()
    return {
        "status": "success",
        "budgets": [
            {"id": b.id, "category": b.category, "limit_amount": b.limit_amount}
            for b in budgets
        ],
    }


@router.post("/limits")
def set_budget_limit(request: BudgetLimitRequest, db: Session = Depends(get_db)):
    """Create or update a budget limit for a category."""
    existing = db.query(models.Budget).filter(
        models.Budget.category == request.category
    ).first()

    if existing:
        existing.limit_amount = request.limit_amount
    else:
        new_budget = models.Budget(
            category=request.category,
            limit_amount=request.limit_amount,
        )
        db.add(new_budget)

    db.commit()
    return {"status": "success", "category": request.category, "limit_amount": request.limit_amount}


@router.get("/summary")
def get_budget_summary(db: Session = Depends(get_db)):
    """Get budget limits with actual spending from transactions."""
    budgets = db.query(models.Budget).all()
    txs = db.query(models.Transaction).all()

    # Aggregate spending by category
    category_spend: Dict[str, float] = {}
    for tx in txs:
        cat = tx.category or "Unknown"
        category_spend[cat] = category_spend.get(cat, 0) + tx.amount

    summary = []
    for b in budgets:
        spent = category_spend.get(b.category, 0)
        ratio = (spent / b.limit_amount * 100) if b.limit_amount > 0 else 0
        summary.append({
            "category": b.category,
            "limit": b.limit_amount,
            "spent": round(spent, 2),
            "ratio": round(ratio, 1),
            "status": "critical" if ratio >= 120 else "exceeded" if ratio >= 100 else "warning" if ratio >= 80 else "ok",
        })

    return {"status": "success", "summary": summary}
