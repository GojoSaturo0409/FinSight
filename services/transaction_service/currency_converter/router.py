from fastapi import APIRouter
from pydantic import BaseModel
from .chain import CurrencyConversionChain

router = APIRouter()


class ConversionRequest(BaseModel):
    amount: float
    base_currency: str
    target_currency: str = "USD"


@router.post("/convert")
def convert_currency(request: ConversionRequest):
    """
    Convert an amount between currencies using the Chain of Responsibility
    fallback: ExchangeRate-API -> Open Exchange Rates -> DB Cache.
    """
    chain = CurrencyConversionChain()
    result = chain.convert(
        amount=request.amount,
        base_currency=request.base_currency.upper(),
        target_currency=request.target_currency.upper(),
    )
    return {"status": "success", **result}


@router.get("/supported")
def get_supported_info():
    """Return info about the currency conversion chain."""
    return {
        "chain_order": [
            "ExchangeRate-API (primary)",
            "Open Exchange Rates (secondary)",
            "Database Cache (terminal fallback)",
        ],
        "note": "If API keys are not set, the chain falls through to the DB cache.",
    }


@router.get("/rates")
def get_all_rates():
    """Return all exchange rates relative to USD for the frontend global CurrencyContext."""
    from .handlers import RedisCachedRateHandler
    return {
        "status": "success",
        "base": "USD",
        "rates": RedisCachedRateHandler.STATIC_RATES_TO_USD,
    }
