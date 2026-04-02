from fastapi import APIRouter
from typing import Dict, Any
from .chain import RecommendationChain

router = APIRouter()
rec_chain = RecommendationChain()

@router.post("/generate")
def generate_recommendations(user_context: Dict[str, Any]):
    recs = rec_chain.get_recommendations(user_context)
    return {"status": "success", "recommendations": recs}
