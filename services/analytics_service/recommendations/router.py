from fastapi import APIRouter, Depends
from typing import Dict, Any
from sqlalchemy.orm import Session
from services.shared.database import get_db
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
def generate_recommendations_auto(db: Session = Depends(get_db)):
    """
    Auto-generate recommendations using real transaction data from DB.
    No frontend context required — everything computed server-side.
    """
    from services.shared.models import Transaction, Budget
    from sqlalchemy import func

    # Compute total spending
    total_spend_result = db.query(func.sum(Transaction.amount)).scalar()
    total_spend = float(total_spend_result or 0)

    # Compute category-level spending
    cat_results = (
        db.query(
            Transaction.category,
            func.sum(Transaction.amount).label('total'),
        )
        .filter(Transaction.category.isnot(None))
        .group_by(Transaction.category)
        .all()
    )
    categories = {row.category: round(float(row.total), 2) for row in cat_results}

    # Detect recurring merchants (merchants that appear 2+ times)
    merchant_counts = (
        db.query(
            Transaction.merchant,
            func.count(Transaction.id).label('count'),
        )
        .filter(Transaction.merchant.isnot(None))
        .group_by(Transaction.merchant)
        .having(func.count(Transaction.id) >= 2)
        .all()
    )
    recurring_merchants = [row.merchant for row in merchant_counts]

    # Get savings target from budget if set
    savings_target = 1500  # default

    # Build real context from DB data
    user_context = {
        "monthly_income": 5000,  # Would come from user profile in production
        "monthly_spend": total_spend,
        "savings_target": savings_target,
        "categories": categories,
        "recurring_merchants": recurring_merchants,
    }

    recs = rec_chain.get_recommendations(user_context, db=db)
    return {
        "status": "success",
        "recommendations": recs,
        "context_used": user_context,
    }
