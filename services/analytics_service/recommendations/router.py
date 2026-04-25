from fastapi import APIRouter, Depends
from typing import Dict, Any
from sqlalchemy.orm import Session
from services.shared.database import get_db
from services.auth_service.auth.router import get_current_user
from .chain import RecommendationChain

router = APIRouter()
rec_chain = RecommendationChain()


@router.post("/generate")
def generate_recommendations(user_context: Dict[str, Any], db: Session = Depends(get_db)):
    """
    Generate personalized financial recommendations based on user context.
    Runs the Chain of Responsibility: HighSpend -> Subscriptions -> SavingsGoal -> Investment.
    """
    recs = rec_chain.get_recommendations(user_context, db=db)
    return {"status": "success", "recommendations": recs}


@router.get("/generate-auto")
def generate_recommendations_auto(db: Session = Depends(get_db), current_user: Any = Depends(get_current_user)):
    """
    Auto-generate recommendations using real transaction data from DB.
    No frontend context required — everything computed server-side.
    """
    from services.shared.models import Transaction, Budget
    from sqlalchemy import func

    from datetime import datetime, timedelta

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    # Base query for user and last 30 days
    base_query = db.query(Transaction).filter(
        Transaction.user_id == current_user.id,
        Transaction.date >= thirty_days_ago
    )

    # Compute total discretionary spending (exclude Income)
    total_spend_result = base_query.filter(Transaction.category != 'Income').with_entities(func.sum(Transaction.amount)).scalar()
    total_spend = float(total_spend_result or 0)

    # Compute income from Income category
    total_income_result = base_query.filter(Transaction.category == 'Income').with_entities(func.sum(Transaction.amount)).scalar()
    total_income = float(total_income_result or 0)
    if total_income == 0:
        total_income = 5000.0  # Fallback if no income transactions exist

    # Compute category-level spending
    cat_results = (
        db.query(
            Transaction.category,
            func.sum(Transaction.amount).label('total'),
        )
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= thirty_days_ago,
            Transaction.category.isnot(None),
            Transaction.category != 'Income'
        )
        .group_by(Transaction.category)
        .all()
    )
    categories = {row.category: round(float(row.total), 2) for row in cat_results}

    # Detect recurring merchants (merchants that appear 2+ times in last 30 days)
    merchant_counts = (
        db.query(
            Transaction.merchant,
            func.count(Transaction.id).label('count'),
        )
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.date >= thirty_days_ago,
            Transaction.merchant.isnot(None),
            Transaction.category != 'Income'
        )
        .group_by(Transaction.merchant)
        .having(func.count(Transaction.id) >= 2)
        .all()
    )
    recurring_merchants = [row.merchant for row in merchant_counts]

    # Get savings target from budget if set
    savings_target = 1500  # default

    # Build real context from DB data
    user_context = {
        "monthly_income": total_income,
        "monthly_spend": total_spend,
        "savings_target": savings_target,
        "categories": categories,
        "recurring_merchants": recurring_merchants,
    }

    recs = rec_chain.get_recommendations(user_context, db=db)
    
    # Remove DB session before returning context to avoid JSON serialization recursion errors
    if "_db_session" in user_context:
        del user_context["_db_session"]

    return {
        "status": "success",
        "recommendations": recs,
        "context_used": user_context,
    }
