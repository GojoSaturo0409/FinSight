import os
import json
import httpx
import datetime
from sqlalchemy.orm import Session

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

# Default demo symbols for the prototype
DEFAULT_SYMBOLS = ["SPY", "BND", "VTI"]

CACHE_MAX_AGE_HOURS = 24


class AlphaVantageService:
    """Service for fetching investment data from Alpha Vantage with DB cache fallback."""

    @staticmethod
    def get_daily_price(symbol: str) -> dict:
        """
        Fetch TIME_SERIES_DAILY data from Alpha Vantage for a given symbol.
        Returns a dict with price, trend, and daily_prices (last 30 days).
        Raises an exception on failure so callers can fall back to cache.
        """
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": ALPHA_VANTAGE_API_KEY,
            "outputsize": "compact",  # last 100 data points
        }

        response = httpx.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Alpha Vantage returns error messages in JSON on rate-limit
        if "Error Message" in data or "Note" in data or "Information" in data:
            raise ValueError(f"Alpha Vantage API error for {symbol}: {data}")

        time_series = data.get("Time Series (Daily)", {})
        if not time_series:
            raise ValueError(f"No time series data returned for {symbol}")

        # Sort by date descending
        sorted_dates = sorted(time_series.keys(), reverse=True)
        latest_date = sorted_dates[0]
        prev_date = sorted_dates[1] if len(sorted_dates) > 1 else latest_date

        latest_close = float(time_series[latest_date]["4. close"])
        prev_close = float(time_series[prev_date]["4. close"])

        trend = "up" if latest_close >= prev_close else "down"
        change_pct = ((latest_close - prev_close) / prev_close) * 100 if prev_close else 0

        # Extract last 30 days for chart rendering
        daily_prices = {}
        for date_str in sorted_dates[:30]:
            daily_prices[date_str] = float(time_series[date_str]["4. close"])

        return {
            "symbol": symbol,
            "price": round(latest_close, 2),
            "trend": trend,
            "change_pct": round(change_pct, 2),
            "daily_prices": daily_prices,
        }

    @staticmethod
    def get_cached_or_fetch(symbol: str, db: Session) -> dict:
        """
        Check InvestmentCache first. If fresh (< CACHE_MAX_AGE_HOURS), return cached.
        Otherwise fetch from Alpha Vantage API and update cache.
        On API failure, return stale cached data with stale=True flag.
        """
        from shared.models import InvestmentCache

        cached = db.query(InvestmentCache).filter(InvestmentCache.symbol == symbol).first()

        # Check if cache is fresh
        if cached and cached.last_updated:
            age = datetime.datetime.utcnow() - cached.last_updated
            if age.total_seconds() < CACHE_MAX_AGE_HOURS * 3600:
                daily_prices = {}
                if cached.daily_prices:
                    try:
                        daily_prices = json.loads(cached.daily_prices)
                    except json.JSONDecodeError:
                        daily_prices = {}

                return {
                    "symbol": cached.symbol,
                    "price": cached.price,
                    "trend": cached.trend or "neutral",
                    "change_pct": 0.0,
                    "daily_prices": daily_prices,
                    "stale": False,
                }

        # Try fetching fresh data from Alpha Vantage
        try:
            fresh_data = AlphaVantageService.get_daily_price(symbol)

            # Update or create cache entry
            if cached:
                cached.price = fresh_data["price"]
                cached.trend = fresh_data["trend"]
                cached.daily_prices = json.dumps(fresh_data["daily_prices"])
                cached.last_updated = datetime.datetime.utcnow()
            else:
                new_cache = InvestmentCache(
                    symbol=symbol,
                    price=fresh_data["price"],
                    trend=fresh_data["trend"],
                    daily_prices=json.dumps(fresh_data["daily_prices"]),
                    last_updated=datetime.datetime.utcnow(),
                )
                db.add(new_cache)

            db.commit()
            fresh_data["stale"] = False
            return fresh_data

        except Exception:
            # API failed — return stale cache if available
            if cached:
                daily_prices = {}
                if cached.daily_prices:
                    try:
                        daily_prices = json.loads(cached.daily_prices)
                    except json.JSONDecodeError:
                        daily_prices = {}

                return {
                    "symbol": cached.symbol,
                    "price": cached.price,
                    "trend": cached.trend or "neutral",
                    "change_pct": 0.0,
                    "daily_prices": daily_prices,
                    "stale": True,
                }

            # No cache, no API — return a minimal fallback
            return {
                "symbol": symbol,
                "price": 0.0,
                "trend": "unknown",
                "change_pct": 0.0,
                "daily_prices": {},
                "stale": True,
            }

    @staticmethod
    def get_portfolio_summary(symbols: list, db: Session) -> list:
        """Fetch data for multiple symbols using the cache-first strategy."""
        results = []
        for symbol in symbols:
            data = AlphaVantageService.get_cached_or_fetch(symbol, db)
            results.append(data)
        return results
