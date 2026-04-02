from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from .factory import TransactionFactory
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from currency_converter.chain import CurrencyConversionChain

router = APIRouter()
converter_chain = CurrencyConversionChain()

@router.post("/sync")
def sync_transactions(source: str, data: List[Dict[str, Any]]):
    try:
        # FACTORY & ADAPTER PATTERNS
        parser = TransactionFactory.create_parser(source, data)
        parsed_transactions = parser.fetch_transactions()

        # Normalization and Currency Conversion (CHAIN OF RESPONSIBILITY)
        for tx in parsed_transactions:
            if tx["currency"] != "USD":
                tx["amount"] = converter_chain.convert(tx["amount"], tx["currency"], "USD")
                tx["currency"] = "USD"
        
        # Here we would typically save them to the database
        # For prototype, we'll return the parsed & normalized transactions
        return {"status": "success", "count": len(parsed_transactions), "data": parsed_transactions}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
