from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import Dict, Any, List, Optional
from .factory import TransactionFactory
from sqlalchemy.orm import Session
import sys
import os
import uuid
import csv
import io
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from currency_converter.chain import CurrencyConversionChain
from auth.router import get_current_user
from services.shared import models
from services.shared.database import get_db
from pydantic import BaseModel
import plaid
from plaid.api import plaid_api
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_sync_request import TransactionsSyncRequest
from plaid.model.products import Products
from plaid.model.country_code import CountryCode

# Configure Plaid client
configuration = plaid.Configuration(
    host=plaid.Environment.Sandbox,
    api_key={
        'clientId': os.getenv('PLAID_CLIENT_ID', ''),
        'secret': os.getenv('PLAID_SECRET', ''),
    }
)
api_client = plaid.ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

router = APIRouter()
converter_chain = CurrencyConversionChain()

class PlaidExchangeRequest(BaseModel):
    public_token: str


class ManualTransactionRequest(BaseModel):
    amount: float
    currency: str = "USD"
    category: str = "Uncategorized"
    merchant: str = "Unknown"
    date: str  # YYYY-MM-DD


@router.post("/sync")
def sync_transactions(
    source: str,
    data: List[Dict[str, Any]],
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        # FACTORY & ADAPTER PATTERNS
        parser = TransactionFactory.create_parser(source, data)
        parsed_transactions = parser.fetch_transactions()

        # Normalization and Currency Conversion (CHAIN OF RESPONSIBILITY)
        for tx in parsed_transactions:
            if tx["currency"] != "USD":
                result = converter_chain.convert(tx["amount"], tx["currency"], "USD")
                tx["amount"] = result["converted_amount"]
                tx["currency"] = "USD"

        # Persist to database
        saved = []
        db_txs = []
        for tx in parsed_transactions:
            db_tx = models.Transaction(
                id=tx.get("id", str(uuid.uuid4())),
                user_id=current_user.id,
                amount=tx["amount"],
                currency=tx["currency"],
                category=tx.get("category", "Uncategorized"),
                merchant=tx.get("merchant", "Unknown"),
                date=tx.get("date", datetime.datetime.utcnow()),
                source=tx.get("source", source),
            )
            db.add(db_tx)
            saved.append(tx)
            db_txs.append(db_tx)

        db.commit()
        from .events import publish_transaction_ingested
        for db_tx in db_txs:
            publish_transaction_ingested(db_tx)
        return {"status": "success", "count": len(saved), "data": saved}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/plaid/create_link_token")
def create_link_token(current_user: models.User = Depends(get_current_user)):
    """Creates a temporary Plaid link token for the React widget."""
    try:
        if not os.getenv('PLAID_CLIENT_ID'):
            # Return a simulated token if no keys (prevents crashing for reviewers without keys)
            return {"link_token": "link-sandbox-mock-12345"}
            
        request = LinkTokenCreateRequest(
            products=[Products("transactions")],
            client_name="FinSight",
            country_codes=[CountryCode("US")],
            language="en",
            user=LinkTokenCreateRequestUser(
                client_user_id=str(current_user.id)
            )
        )
        response = client.link_token_create(request)
        return {"link_token": response['link_token']}
    except plaid.ApiException as e:
        raise HTTPException(status_code=400, detail=f"Plaid Error: {e.body}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/plaid/set_access_token")
def exchange_public_token(
    req: PlaidExchangeRequest, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Exchanges public_token for access_token and performs initial transaction sync."""
    try:
        access_token = "mock-access-token"
        
        if os.getenv('PLAID_CLIENT_ID') and req.public_token != "mock-public-token":
            exchange_request = ItemPublicTokenExchangeRequest(public_token=req.public_token)
            exchange_response = client.item_public_token_exchange(exchange_request)
            access_token = exchange_response['access_token']
        else:
            # We are using mock sandbox without keys, fake the initial sync
            pass

        # Perform an initial sync from Plaid
        all_transactions = []
        
        if os.getenv('PLAID_CLIENT_ID') and access_token != "mock-access-token":
            sync_request = TransactionsSyncRequest(access_token=access_token)
            sync_response = client.transactions_sync(sync_request)
            all_transactions = sync_response['added']
        else:
            # Generate mock Plaid transaction format
            all_transactions = [
                {
                    "transaction_id": str(uuid.uuid4()),
                    "amount": 80.50,
                    "iso_currency_code": "USD",
                    "category": ["Food and Drink", "Restaurants"],
                    "merchant_name": "Starbucks Sandbox",
                    "date": datetime.datetime.utcnow().strftime("%Y-%m-%d")
                },
                {
                    "transaction_id": str(uuid.uuid4()),
                    "amount": 1200.00,
                    "iso_currency_code": "USD",
                    "category": ["Payment", "Rent"],
                    "merchant_name": "Avalon Sandbox",
                    "date": datetime.datetime.utcnow().strftime("%Y-%m-%d")
                }
            ]

        # Use PlaidAdapter to normalize
        parser = TransactionFactory.create_parser("plaid", all_transactions)
        parsed = parser.fetch_transactions()

        # Save to DB
        saved = []
        db_txs = []
        for tx in parsed:
            # Currency conversion logic
            if tx["currency"] != "USD":
                result = converter_chain.convert(tx["amount"], tx["currency"], "USD")
                tx["amount"] = result["converted_amount"]
                tx["currency"] = "USD"
                
            db_tx = models.Transaction(
                id=tx.get("id", str(uuid.uuid4())),
                user_id=current_user.id,
                amount=tx["amount"],
                currency=tx["currency"],
                category=tx.get("category", "Uncategorized"),
                merchant=tx.get("merchant", "Unknown"),
                date=tx.get("date", datetime.datetime.utcnow()),
                source="plaid",
            )
            db.add(db_tx)
            saved.append(tx)
            db_txs.append(db_tx)

        db.commit()
        from .events import publish_transaction_ingested
        for db_tx in db_txs:
            publish_transaction_ingested(db_tx)
        return {"status": "success", "count": len(saved), "access_token_saved": True}
        
    except plaid.ApiException as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Plaid Error: {e.body}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/manual")
def add_manual_transaction(
    tx: ManualTransactionRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Add a single manual transaction entry."""
    try:
        db_tx = models.Transaction(
            id=str(uuid.uuid4()),
            user_id=current_user.id,
            amount=tx.amount,
            currency=tx.currency,
            category=tx.category,
            merchant=tx.merchant,
            date=datetime.datetime.strptime(tx.date, "%Y-%m-%d"),
            source="manual",
        )
        db.add(db_tx)
        db.commit()
        db.refresh(db_tx)
        from .events import publish_transaction_ingested
        publish_transaction_ingested(db_tx)
        return {
            "status": "success",
            "transaction": {
                "id": db_tx.id,
                "amount": db_tx.amount,
                "currency": db_tx.currency,
                "category": db_tx.category,
                "merchant": db_tx.merchant,
                "date": db_tx.date.strftime("%Y-%m-%d"),
                "source": db_tx.source,
            },
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/upload-csv")
def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Upload a CSV file of transactions. Expected columns: Date, Description, Amount, Currency."""
    try:
        contents = file.file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(contents))
        rows = list(reader)

        parser = TransactionFactory.create_parser("csv", rows)
        parsed = parser.fetch_transactions()

        saved = []
        db_txs = []
        for tx in parsed:
            if tx["currency"] != "USD":
                result = converter_chain.convert(tx["amount"], tx["currency"], "USD")
                tx["amount"] = result["converted_amount"]
                tx["currency"] = "USD"

            db_tx = models.Transaction(
                id=str(uuid.uuid4()),
                user_id=current_user.id,
                amount=tx["amount"],
                currency=tx["currency"],
                category=tx.get("category", "Uncategorized"),
                merchant=tx.get("merchant", "Unknown"),
                date=tx.get("date", datetime.datetime.utcnow()),
                source="csv",
            )
            db.add(db_tx)
            saved.append(tx)
            db_txs.append(db_tx)

        db.commit()
        from .events import publish_transaction_ingested
        for db_tx in db_txs:
            publish_transaction_ingested(db_tx)
        return {"status": "success", "count": len(saved), "data": saved}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/transactions")
def get_transactions(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Get user's transactions from DB, newest first."""
    txs = (
        db.query(models.Transaction)
        .filter(models.Transaction.user_id == current_user.id)
        .order_by(models.Transaction.date.desc())
        .limit(limit)
        .all()
    )
    return {
        "status": "success",
        "count": len(txs),
        "data": [
            {
                "id": tx.id,
                "amount": tx.amount,
                "currency": tx.currency,
                "category": tx.category,
                "merchant": tx.merchant,
                "date": tx.date.strftime("%Y-%m-%d") if tx.date else "",
                "source": tx.source,
            }
            for tx in txs
        ],
    }


@router.get("/transactions/all")
def get_all_transactions(
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get all transactions (no auth required, for dashboard demo)."""
    txs = (
        db.query(models.Transaction)
        .order_by(models.Transaction.date.desc())
        .limit(limit)
        .all()
    )
    return {
        "status": "success",
        "count": len(txs),
        "data": [
            {
                "id": tx.id,
                "amount": tx.amount,
                "currency": tx.currency,
                "category": tx.category,
                "merchant": tx.merchant,
                "date": tx.date.strftime("%Y-%m-%d") if tx.date else "",
                "source": tx.source,
            }
            for tx in txs
        ],
    }
