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

# Realistic mock stock data for when no API key is available
MOCK_STOCK_DB = {
    "SPY": {"price": 523.40, "trend": "up", "change_pct": 0.43, "name": "S&P 500 ETF"},
    "BND": {"price": 72.85, "trend": "up", "change_pct": 0.21, "name": "Vanguard Bond ETF"},
    "VTI": {"price": 261.20, "trend": "up", "change_pct": 0.54, "name": "Vanguard Total Market"},
    "AAPL": {"price": 189.84, "trend": "up", "change_pct": 1.12, "name": "Apple Inc."},
    "TSLA": {"price": 172.50, "trend": "down", "change_pct": -2.30, "name": "Tesla Inc."},
    "GOOGL": {"price": 155.72, "trend": "up", "change_pct": 0.85, "name": "Alphabet Inc."},
    "MSFT": {"price": 420.55, "trend": "up", "change_pct": 0.67, "name": "Microsoft Corp."},
    "AMZN": {"price": 185.30, "trend": "up", "change_pct": 1.45, "name": "Amazon.com Inc."},
    "NVDA": {"price": 880.40, "trend": "up", "change_pct": 3.20, "name": "NVIDIA Corp."},
    "META": {"price": 505.20, "trend": "up", "change_pct": 0.95, "name": "Meta Platforms"},
}


def _generate_mock_daily_prices(base_price: float, days: int = 30) -> dict:
    """Generate realistic-looking daily price history."""
    import random
    random.seed(int(base_price * 100))  # deterministic per stock
    prices = {}
    price = base_price * 0.95  # start ~5% lower
    today = datetime.datetime.utcnow()
    for i in range(days, 0, -1):
        date_str = (today - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
        change = random.uniform(-0.015, 0.02) * price
        price = round(price + change, 2)
        prices[date_str] = price
    # ensure final price matches base
    prices[today.strftime("%Y-%m-%d")] = base_price
    return prices


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
        Check InvestmentCache first. If fresh (<CACHE_MAX_AGE_HOURS), return cached.
        Otherwise fetch from Alpha Vantage API and update cache.
        On API failure, return stale cached data or realistic mock data.
        """
        from services.shared.models import InvestmentCache

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

            # No cache, no API — return realistic mock data
            mock = MOCK_STOCK_DB.get(symbol.upper())
            if mock:
                daily_prices = _generate_mock_daily_prices(mock["price"])
                # Persist mock data to cache for next time
                try:
                    new_cache = InvestmentCache(
                        symbol=symbol,
                        price=mock["price"],
                        trend=mock["trend"],
                        daily_prices=json.dumps(daily_prices),
                        last_updated=datetime.datetime.utcnow(),
                    )
                    db.add(new_cache)
                    db.commit()
                except Exception:
                    db.rollback()

                return {
                    "symbol": symbol,
                    "price": mock["price"],
                    "trend": mock["trend"],
                    "change_pct": mock["change_pct"],
                    "daily_prices": daily_prices,
                    "name": mock["name"],
                    "stale": False,
                }

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
            # Add name from MOCK_STOCK_DB if available
            if "name" not in data:
                mock = MOCK_STOCK_DB.get(symbol.upper())
                data["name"] = mock["name"] if mock else f"{symbol} ETF"
            results.append(data)
        return results

    @staticmethod
    def search_stocks(query: str) -> list:
        """Search for stocks by symbol or name."""
        query = query.upper()
        results = []
        for symbol, info in MOCK_STOCK_DB.items():
            if query in symbol or query.lower() in info["name"].lower():
                results.append({
                    "symbol": symbol,
                    "name": info["name"],
                    "price": info["price"],
                    "trend": info["trend"],
                    "change_pct": info["change_pct"],
                })
        return results
