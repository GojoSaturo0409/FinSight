from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from typing import Dict, Any, List, Optional
from .factory import TransactionFactory
from sqlalchemy.orm import Session
import os
import uuid
import csv
import io
import datetime

from services.transaction_service.currency_converter.chain import CurrencyConversionChain
from services.auth_service.auth.router import get_current_user
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
            products=[Products("transactions"), Products("investments")],
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
    import time as _time

    try:
        if req.public_token == 'mock-public-token-123' or not os.getenv('PLAID_CLIENT_ID'):
            # The user triggered the simulated flow because they lack Sandbox keys.
            return {"status": "success", "count": 0, "access_token_saved": True, "message": "Mock login successful. Use 'Load Default Data' for simulation."}

        exchange_request = ItemPublicTokenExchangeRequest(public_token=req.public_token)
        exchange_response = client.item_public_token_exchange(exchange_request)
        access_token = exchange_response['access_token']

        # Save the access token on the user for future syncs
        current_user.plaid_access_token = access_token
        db.commit()

        # --- Retry loop: Sandbox prepares data asynchronously ---
        all_transactions = []
        for attempt in range(5):
            sync_request = TransactionsSyncRequest(access_token=access_token)
            sync_response = client.transactions_sync(sync_request)
            all_transactions = sync_response['added']
            if len(all_transactions) > 0:
                break
            _time.sleep(3)  # Wait for sandbox to prepare data

        # Get accounts info for balances
        from plaid.model.accounts_get_request import AccountsGetRequest
        accounts_request = AccountsGetRequest(access_token=access_token)
        accounts_response = client.accounts_get(accounts_request)
        all_accounts = accounts_response['accounts']

        # Use PlaidAdapter to normalize
        parser = TransactionFactory.create_parser("plaid", {"transactions": all_transactions, "accounts": all_accounts})
        parsed = parser.fetch_transactions()

        # Save transactions to DB
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
                source=tx.get("source", "plaid"),
            )
            existing = db.query(models.Transaction).filter_by(id=db_tx.id).first()
            if not existing:
                db.add(db_tx)
                saved.append(tx)
                db_txs.append(db_tx)

        # --- Fetch Investment Holdings ---
        inv_count = 0
        try:
            from plaid.model.investments_holdings_get_request import InvestmentsHoldingsGetRequest
            inv_request = InvestmentsHoldingsGetRequest(access_token=access_token)
            inv_response = client.investments_holdings_get(inv_request)
            holdings = inv_response.get('holdings', [])
            securities = {s['security_id']: s for s in inv_response.get('securities', [])}

            for holding in holdings:
                sec = securities.get(holding.get('security_id', ''), {})
                symbol = sec.get('ticker_symbol', 'UNKNOWN')
                if not symbol or symbol == 'UNKNOWN':
                    continue

                shares = float(holding.get('quantity', 0))
                price = float(holding.get('institution_price', 0))

                existing_inv = db.query(models.Investment).filter(
                    models.Investment.user_id == current_user.id,
                    models.Investment.symbol == symbol
                ).first()

                if existing_inv:
                    existing_inv.shares = shares
                    existing_inv.average_price = price
                    existing_inv.last_updated = datetime.datetime.utcnow()
                else:
                    new_inv = models.Investment(
                        user_id=current_user.id,
                        symbol=symbol,
                        shares=shares,
                        average_price=price,
                        last_updated=datetime.datetime.utcnow(),
                    )
                    db.add(new_inv)
                inv_count += 1
        except Exception as inv_err:
            # Investment fetch may fail (e.g., product not available); don't block transactions
            print(f"Investment fetch warning: {inv_err}")

        db.commit()
        from .events import publish_transaction_ingested
        for db_tx in db_txs:
            publish_transaction_ingested(db_tx)
        return {"status": "success", "count": len(saved), "investments": inv_count, "access_token_saved": True}
        
    except plaid.ApiException as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=f"Plaid Error: {e.body}")
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
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

@router.post("/demo-data")
def load_demo_data(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Loads a set of realistic 3-month demo transactions for testing."""
    import uuid
    from datetime import timedelta
    
    test_data = []
    base_date = datetime.datetime.utcnow()
    
    # Generate 24 transactions distributed over the last 90 days
    categories = ["Food", "Transport", "Entertainment", "Shopping", "Utilities"]
    merchants = ["Whole Foods", "Uber", "Netflix", "Amazon", "ConEdison"]
    amounts = [45.50, 12.00, 15.99, 120.00, 85.00]
    
    for i in range(24):
        days_ago = (i * 3) + 1  # spread out over ~75 days
        tx_date = base_date - timedelta(days=days_ago)
        
        # Add income every ~8 transactions (representing monthly salary)
        if i % 8 == 0:
            test_data.append({
                "id": str(uuid.uuid4()),
                "amount": 5000.00,
                "currency": "USD",
                "category": "Income",
                "merchant": "TechCorp Salary",
                "date": tx_date.isoformat(),
                "source": "demo"
            })
        else:
            idx = i % 5
            test_data.append({
                "id": str(uuid.uuid4()),
                "amount": amounts[idx],
                "currency": "USD",
                "category": categories[idx],
                "merchant": merchants[idx],
                "date": tx_date.isoformat(),
                "source": "demo"
            })
    
    saved = []
    db_txs = []
    try:
        for tx in test_data:
            db_tx = models.Transaction(
                id=tx["id"],
                user_id=current_user.id,
                amount=tx["amount"],
                currency=tx["currency"],
                category=tx["category"],
                merchant=tx["merchant"],
                date=datetime.datetime.fromisoformat(tx["date"].replace('Z', '+00:00')),
                source=tx["source"],
            )
            # check if exists
            existing = db.query(models.Transaction).filter_by(id=db_tx.id).first()
            if not existing:
                db.add(db_tx)
                saved.append(tx)
                db_txs.append(db_tx)
        
        db.commit()
        from .events import publish_transaction_ingested
        for db_tx in db_txs:
            publish_transaction_ingested(db_tx)
            
        return {"status": "success", "count": len(saved), "message": "Demo data loaded."}
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
