from fastapi import APIRouter
from typing import List, Dict, Any
from .service import CategorizationService
from .strategies import RuleBasedStrategy, MLStrategy

router = APIRouter()

@router.post("/categorize")
def categorize_transactions(transactions: List[Dict[str, Any]], strategy_type: str = "rule"):
    # Determine strategy to use
    if strategy_type.lower() == "ml":
        strategy = MLStrategy()
    else:
        strategy = RuleBasedStrategy()
        
    service = CategorizationService(strategy=strategy)
    categorized_txs = service.process_transactions(transactions)
    
    return {"status": "success", "count": len(categorized_txs), "data": categorized_txs}
