from fastapi import APIRouter
from typing import List, Dict, Any
from .service import CategorizationService, get_default_service
from .strategies import RuleBasedStrategy, MLStrategy

router = APIRouter()

# Config-driven default service (reads CATEGORIZATION_STRATEGY env var)
_default_service = get_default_service()


@router.post("/categorize")
def categorize_transactions(transactions: List[Dict[str, Any]], strategy_type: str = ""):
    """
    Categorize a batch of transactions.
    
    - If strategy_type is provided ('rule' or 'ml'), use that strategy for this request.
    - Otherwise, use the config-driven default strategy.
    """
    if strategy_type:
        # Per-request override
        if strategy_type.lower() == "ml":
            strategy = MLStrategy()
        else:
            strategy = RuleBasedStrategy()
        service = CategorizationService(strategy=strategy)
    else:
        service = _default_service

    categorized_txs = service.process_transactions(transactions)

    return {
        "status": "success",
        "strategy_used": service.current_strategy_name,
        "count": len(categorized_txs),
        "data": categorized_txs,
    }


@router.get("/strategy")
def get_current_strategy():
    """Return the currently configured default strategy."""
    return {
        "current_strategy": _default_service.current_strategy_name,
    }
