from fastapi import APIRouter, Depends
from typing import Dict, Any
from sqlalchemy.orm import Session
from database import get_db
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
