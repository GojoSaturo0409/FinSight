from abc import ABC, abstractmethod

class BaseRateHandler(ABC):
    def __init__(self):
        self._next_handler = None

    def set_next(self, handler: 'BaseRateHandler') -> 'BaseRateHandler':
        self._next_handler = handler
        return handler

    @abstractmethod
    def handle(self, currency_pair: str) -> float:
        if self._next_handler:
            return self._next_handler.handle(currency_pair)
        
        # If no handler could resolve the rate
        return 1.0 # default fallback

class ExchangeRateAPIHandler(BaseRateHandler):
    def handle(self, currency_pair: str) -> float:
        # Mocking ExchangeRateAPI failure for some pairs to trigger failover
        if "USD_EUR" in currency_pair:
            return 0.85
        if "FAIL" in currency_pair:
            # Simulate failure and pass to next handler
            if self._next_handler:
                return self._next_handler.handle(currency_pair)
        return 1.0 # Or pass to next

class OpenExchangeRatesHandler(BaseRateHandler):
    def handle(self, currency_pair: str) -> float:
        # Mocking OpenExchangeRates logic
        if "USD_GBP" in currency_pair:
            return 0.75
        
        # If it fails, pass it down
        if self._next_handler:
            return getattr(self._next_handler, 'handle')(currency_pair)
        return 1.0

class DBCachedRateHandler(BaseRateHandler):
    def handle(self, currency_pair: str) -> float:
        # Mock DB retrieval for terminal fallback
        mock_db_cache = {
             "USD_INR": 83.5,
             "USD_JPY": 150.0
        }
        return mock_db_cache.get(currency_pair, 1.0)
