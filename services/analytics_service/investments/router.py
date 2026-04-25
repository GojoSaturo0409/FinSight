from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from services.shared.database import get_db
from .alpha_vantage_service import AlphaVantageService, DEFAULT_SYMBOLS

router = APIRouter()


@router.get("/portfolio")
def get_portfolio(db: Session = Depends(get_db)):
    """
    Returns current prices and trends for the default demo portfolio symbols (SPY, BND, VTI).
    Uses cached data when available, falling back to Alpha Vantage API.
    """
    portfolio = AlphaVantageService.get_portfolio_summary(DEFAULT_SYMBOLS, db)
    return {"status": "success", "portfolio": portfolio}


@router.get("/quote/{symbol}")
def get_quote(symbol: str, db: Session = Depends(get_db)):
    """
    Returns a single stock quote with trend data.
    Checks cache first, then fetches from Alpha Vantage if stale.
    """
    data = AlphaVantageService.get_cached_or_fetch(symbol.upper(), db)
    return {"status": "success", "quote": data}
