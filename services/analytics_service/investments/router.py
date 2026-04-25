from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import uuid
import datetime
from services.shared.database import get_db
from services.shared import models
from services.auth_service.auth.router import get_current_user
from .alpha_vantage_service import AlphaVantageService, DEFAULT_SYMBOLS

router = APIRouter()

class TradeRequest(BaseModel):
    symbol: str
    shares: float


@router.get("/portfolio")
def get_portfolio(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Returns current prices and trends for the user's actual portfolio.
    If the user has no investments, returns an empty list.
    """
    investments = db.query(models.Investment).filter(models.Investment.user_id == current_user.id).all()
    
    portfolio = []
    for inv in investments:
        if inv.shares <= 0:
            continue
            
        data = AlphaVantageService.get_cached_or_fetch(inv.symbol, db)
        # Add name from MOCK_STOCK_DB if available
        if "name" not in data:
            from .alpha_vantage_service import MOCK_STOCK_DB
            mock = MOCK_STOCK_DB.get(inv.symbol.upper())
            data["name"] = mock["name"] if mock else f"{inv.symbol} ETF"
            
        data["shares"] = inv.shares
        data["average_price"] = inv.average_price
        data["total_value"] = inv.shares * data["price"]
        portfolio.append(data)
        
    return {"status": "success", "portfolio": portfolio}

@router.post("/buy")
def buy_investment(
    req: TradeRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    symbol = req.symbol.upper()
    if req.shares <= 0:
        raise HTTPException(status_code=400, detail="Cannot buy 0 or negative shares")
        
    # Get current price
    data = AlphaVantageService.get_cached_or_fetch(symbol, db)
    current_price = data["price"]
    if current_price <= 0:
        raise HTTPException(status_code=400, detail=f"Invalid price for {symbol}")
        
    cost = current_price * req.shares
    
    # 1. Update / Create Investment
    inv = db.query(models.Investment).filter(
        models.Investment.user_id == current_user.id,
        models.Investment.symbol == symbol
    ).first()
    
    if inv:
        # Weighted average price
        total_cost = (inv.shares * inv.average_price) + cost
        inv.shares += req.shares
        inv.average_price = total_cost / inv.shares
        inv.last_updated = datetime.datetime.utcnow()
    else:
        inv = models.Investment(
            user_id=current_user.id,
            symbol=symbol,
            shares=req.shares,
            average_price=current_price
        )
        db.add(inv)
        
    # 2. Add Transaction to subtract from cash balance
    tx = models.Transaction(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        amount=cost,
        currency="USD",
        category="Investment",
        merchant=f"Bought {req.shares} shs of {symbol}",
        date=datetime.datetime.utcnow(),
        source="platform"
    )
    db.add(tx)
    
    db.commit()
    return {"status": "success", "message": f"Bought {req.shares} of {symbol}", "cost": cost}

@router.post("/sell")
def sell_investment(
    req: TradeRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    symbol = req.symbol.upper()
    if req.shares <= 0:
        raise HTTPException(status_code=400, detail="Cannot sell 0 or negative shares")
        
    inv = db.query(models.Investment).filter(
        models.Investment.user_id == current_user.id,
        models.Investment.symbol == symbol
    ).first()
    
    if not inv or inv.shares < req.shares:
        raise HTTPException(status_code=400, detail=f"Not enough shares of {symbol} to sell. Owned: {inv.shares if inv else 0}")
        
    # Get current price
    data = AlphaVantageService.get_cached_or_fetch(symbol, db)
    current_price = data["price"]
    proceeds = current_price * req.shares
    
    # 1. Update Investment
    inv.shares -= req.shares
    inv.last_updated = datetime.datetime.utcnow()
    
    # 2. Add Transaction to add to cash balance (Negative amount = Income/Deposit in some logic, but wait: dashboard reads totalSpend as sum of tx != 'Income' and positive amount. Wait!)
    # FinSight treats positive transaction amount as an *expense* generally unless category=='Income'.
    # For a deposit/income, we should record category="Income" and amount > 0.
    tx = models.Transaction(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        amount=proceeds,
        currency="USD",
        category="Income",
        merchant=f"Sold {req.shares} shs of {symbol}",
        date=datetime.datetime.utcnow(),
        source="platform"
    )
    db.add(tx)
    
    db.commit()
    return {"status": "success", "message": f"Sold {req.shares} of {symbol}", "proceeds": proceeds}


@router.get("/quote/{symbol}")
def get_quote(symbol: str, db: Session = Depends(get_db)):
    """
    Returns a single stock quote with trend data.
    Checks cache first, then fetches from Alpha Vantage if stale.
    """
    data = AlphaVantageService.get_cached_or_fetch(symbol.upper(), db)
    return {"status": "success", "quote": data}


@router.get("/search/{query}")
def search_stocks(query: str):
    """Search for stocks by symbol or name."""
    results = AlphaVantageService.search_stocks(query)
    return {"status": "success", "results": results}


@router.get("/all_stocks")
def get_all_stocks():
    """Return all available stocks for browsing."""
    from .alpha_vantage_service import MOCK_STOCK_DB
    stocks = [
        {"symbol": sym, "name": info["name"], "price": info["price"],
         "trend": info["trend"], "change_pct": info["change_pct"]}
        for sym, info in MOCK_STOCK_DB.items()
    ]
    return {"status": "success", "stocks": stocks}

