from abc import ABC, abstractmethod
import os
import logging

logger = logging.getLogger(__name__)


class BaseRateHandler(ABC):
    """
    Abstract handler in the Chain of Responsibility for currency conversion.
    
    Chain: ExchangeRateAPI -> OpenExchangeRates -> DBCachedRate
    Each handler tries to resolve the rate. On failure, it passes
    the request to the next handler in the chain.
    """

    def __init__(self):
        self._next_handler = None

    def set_next(self, handler: 'BaseRateHandler') -> 'BaseRateHandler':
        """Link the next handler in the chain. Returns the next handler for fluent chaining."""
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, base_currency: str, target_currency: str) -> float:
        """
        Try to resolve the exchange rate. If this handler cannot,
        delegate to the next handler.
        
        Args:
            base_currency: Source currency code (e.g. 'EUR')
            target_currency: Target currency code (e.g. 'USD')
            
        Returns:
            Exchange rate as a float, or 1.0 as the terminal fallback.
        """
        pass

    def _pass_to_next(self, base_currency: str, target_currency: str) -> float:
        """Delegate to the next handler, or return 1.0 if no handler remains."""
        if self._next_handler:
            return self._next_handler.handle(base_currency, target_currency)
        logger.warning("End of chain reached, no handler could resolve %s -> %s. Returning 1.0",
                        base_currency, target_currency)
        return 1.0


class ExchangeRateAPIHandler(BaseRateHandler):
    """
    Primary handler: calls ExchangeRate-API (https://www.exchangerate-api.com/).
    Free tier: 1,500 requests/month.
    
    Env var: EXCHANGERATE_API_KEY
    """

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("EXCHANGERATE_API_KEY", "")

    def handle(self, base_currency: str, target_currency: str) -> float:
        if not self.api_key:
            logger.info("ExchangeRateAPIHandler: No API key configured, passing to next handler")
            return self._pass_to_next(base_currency, target_currency)

        try:
            import httpx

            url = f"https://v6.exchangerate-api.com/v6/{self.api_key}/pair/{base_currency}/{target_currency}"
            response = httpx.get(url, timeout=10.0)

            if response.status_code == 429:
                logger.warning("ExchangeRateAPIHandler: Rate limited (429), falling over to next handler")
                return self._pass_to_next(base_currency, target_currency)

            if response.status_code == 200:
                data = response.json()
                if data.get("result") == "success":
                    rate = data.get("conversion_rate", 1.0)
                    logger.info("ExchangeRateAPIHandler: %s -> %s = %f", base_currency, target_currency, rate)
                    return rate
                else:
                    logger.warning("ExchangeRateAPIHandler: API error: %s", data.get("error-type", "unknown"))
                    return self._pass_to_next(base_currency, target_currency)
            else:
                logger.warning("ExchangeRateAPIHandler: HTTP %d, passing to next", response.status_code)
                return self._pass_to_next(base_currency, target_currency)

        except Exception as e:
            logger.error("ExchangeRateAPIHandler: Request failed: %s", str(e))
            return self._pass_to_next(base_currency, target_currency)


class OpenExchangeRatesHandler(BaseRateHandler):
    """
    Secondary handler: calls Open Exchange Rates (https://openexchangerates.org/).
    Free tier: 1,000 requests/month. Base currency fixed to USD on free plan.
    
    Env var: OPENEXCHANGE_APP_ID
    """

    def __init__(self):
        super().__init__()
        self.app_id = os.getenv("OPENEXCHANGE_APP_ID", "")

    def handle(self, base_currency: str, target_currency: str) -> float:
        if not self.app_id:
            logger.info("OpenExchangeRatesHandler: No APP_ID configured, passing to next handler")
            return self._pass_to_next(base_currency, target_currency)

        try:
            import httpx

            # Free plan only supports USD as base
            url = f"https://openexchangerates.org/api/latest.json?app_id={self.app_id}"
            response = httpx.get(url, timeout=10.0)

            if response.status_code == 429:
                logger.warning("OpenExchangeRatesHandler: Rate limited (429), falling over to next handler")
                return self._pass_to_next(base_currency, target_currency)

            if response.status_code == 200:
                data = response.json()
                rates = data.get("rates", {})

                # OXR returns rates relative to USD
                base_rate = rates.get(base_currency)
                target_rate = rates.get(target_currency)

                if base_rate and target_rate:
                    # Cross rate: target_rate / base_rate
                    rate = target_rate / base_rate
                    logger.info("OpenExchangeRatesHandler: %s -> %s = %f (via USD cross rate)",
                                base_currency, target_currency, rate)
                    return rate
                else:
                    logger.warning("OpenExchangeRatesHandler: Missing rates for %s or %s",
                                    base_currency, target_currency)
                    return self._pass_to_next(base_currency, target_currency)
            else:
                logger.warning("OpenExchangeRatesHandler: HTTP %d, passing to next", response.status_code)
                return self._pass_to_next(base_currency, target_currency)

        except Exception as e:
            logger.error("OpenExchangeRatesHandler: Request failed: %s", str(e))
            return self._pass_to_next(base_currency, target_currency)


class DBCachedRateHandler(BaseRateHandler):
    """
    Terminal handler: reads cached exchange rates from the PostgreSQL database.
    Uses the ExchangeRateCache model via SQLAlchemy session.
    Returns 1.0 as the absolute last fallback if no cache entry exists.
    """

    def __init__(self, db_session=None):
        super().__init__()
        self._db = db_session

    def set_db(self, db_session):
        """Inject DB session (useful for delayed initialization)."""
        self._db = db_session

    def handle(self, base_currency: str, target_currency: str) -> float:
        if self._db is None:
            logger.warning("DBCachedRateHandler: No DB session available, returning default 1.0")
            return self._pass_to_next(base_currency, target_currency)

        try:
            from models import ExchangeRateCache

            pair = f"{base_currency}_{target_currency}"
            cached = self._db.query(ExchangeRateCache).filter(
                ExchangeRateCache.currency_pairs == pair
            ).first()

            if cached:
                logger.info("DBCachedRateHandler: Found cached rate for %s = %f (last updated: %s)",
                            pair, cached.rate, cached.last_updated)
                return cached.rate
            else:
                # Try reverse pair
                reverse_pair = f"{target_currency}_{base_currency}"
                cached_reverse = self._db.query(ExchangeRateCache).filter(
                    ExchangeRateCache.currency_pairs == reverse_pair
                ).first()
                if cached_reverse and cached_reverse.rate != 0:
                    rate = 1.0 / cached_reverse.rate
                    logger.info("DBCachedRateHandler: Found reverse cached rate for %s = %f", pair, rate)
                    return rate

            logger.warning("DBCachedRateHandler: No cache entry for %s, returning 1.0", pair)
            return 1.0

        except Exception as e:
            logger.error("DBCachedRateHandler: DB query failed: %s", str(e))
            return 1.0


def save_rate_to_cache(db_session, base_currency: str, target_currency: str, rate: float):
    """
    Persist a freshly fetched rate to the DB cache for future fallback.
    Called after a successful API response.
    """
    if db_session is None:
        return

    try:
        import datetime
        from models import ExchangeRateCache

        pair = f"{base_currency}_{target_currency}"
        existing = db_session.query(ExchangeRateCache).filter(
            ExchangeRateCache.currency_pairs == pair
        ).first()

        if existing:
            existing.rate = rate
            existing.last_updated = datetime.datetime.utcnow()
        else:
            new_entry = ExchangeRateCache(
                currency_pairs=pair,
                rate=rate,
                last_updated=datetime.datetime.utcnow(),
            )
            db_session.add(new_entry)

        db_session.commit()
        logger.info("Saved rate to cache: %s = %f", pair, rate)

    except Exception as e:
        logger.error("Failed to save rate to cache: %s", str(e))
