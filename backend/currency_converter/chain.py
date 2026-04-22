from .handlers import (
    ExchangeRateAPIHandler,
    OpenExchangeRatesHandler,
    DBCachedRateHandler,
    save_rate_to_cache,
)
import logging

logger = logging.getLogger(__name__)


class CurrencyConversionChain:
    """
    Chain of Responsibility for currency conversion.
    
    Chain order:
      1. ExchangeRate-API (primary, 1500 free req/month)
      2. Open Exchange Rates (secondary, 1000 free req/month)
      3. DB Cached Rate (terminal fallback from PostgreSQL)
    
    When the primary or secondary API succeeds, the result is persisted
    to the DB cache so that the terminal fallback stays updated.
    """

    def __init__(self, db_session=None):
        self._db = db_session

        # Build the handler chain
        self.entry_handler = ExchangeRateAPIHandler()
        open_exchange = OpenExchangeRatesHandler()
        db_cache = DBCachedRateHandler(db_session=db_session)

        # Link: ExchangeRateAPI -> OpenExchangeRates -> DBCache
        self.entry_handler.set_next(open_exchange).set_next(db_cache)

    def convert(self, amount: float, base_currency: str, target_currency: str = "USD") -> dict:
        """
        Convert an amount from base_currency to target_currency.
        
        Returns:
            Dict with 'original_amount', 'converted_amount', 'rate',
            'base_currency', 'target_currency'
        """
        if base_currency == target_currency:
            return {
                "original_amount": amount,
                "converted_amount": amount,
                "rate": 1.0,
                "base_currency": base_currency,
                "target_currency": target_currency,
            }

        rate = self.entry_handler.handle(base_currency, target_currency)

        # Persist to cache if we got a real rate from an API
        if rate != 1.0 and self._db is not None:
            save_rate_to_cache(self._db, base_currency, target_currency, rate)

        converted = round(amount * rate, 2)

        logger.info("CurrencyConversionChain: %.2f %s -> %.2f %s (rate: %f)",
                     amount, base_currency, converted, target_currency, rate)

        return {
            "original_amount": amount,
            "converted_amount": converted,
            "rate": rate,
            "base_currency": base_currency,
            "target_currency": target_currency,
        }
