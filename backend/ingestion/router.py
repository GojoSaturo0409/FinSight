from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from .factory import TransactionFactory
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from currency_converter.chain import CurrencyConversionChain
from auth.router import get_current_user
import models
from fastapi import Depends
from .plaid_client import client as plaid_client
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

router = APIRouter()
converter_chain = CurrencyConversionChain()

@router.post("/sync")
def sync_transactions(source: str, data: List[Dict[str, Any]], current_user: models.User = Depends(get_current_user)):
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

@router.post("/plaid/create_link_token")
def create_link_token(current_user: models.User = Depends(get_current_user)):
    try:
        request = LinkTokenCreateRequest(
            products=[Products("transactions")],
            client_name="FinSight",
            country_codes=[CountryCode("US")],
            language="en",
            user=LinkTokenCreateRequestUser(client_user_id=str(current_user.id))
        )
        response = plaid_client.link_token_create(request)
        return response.to_dict()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/plaid/set_access_token")
def set_access_token(public_token: str, current_user: models.User = Depends(get_current_user)):
    try:
        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = plaid_client.item_public_token_exchange(request)
        access_token = response['access_token']
        # Normally save access_token to user DB here
        return {"msg": "Access token set successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

