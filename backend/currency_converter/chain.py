from .handlers import ExchangeRateAPIHandler, OpenExchangeRatesHandler, DBCachedRateHandler

class CurrencyConversionChain:
    def __init__(self):
        self.entry_handler = ExchangeRateAPIHandler()
        open_exchange = OpenExchangeRatesHandler()
        db_cache = DBCachedRateHandler()

        # Build the chain: ExchangeRateAPI -> OpenExchange Rates -> DB Cache
        self.entry_handler.set_next(open_exchange).set_next(db_cache)

    def convert(self, amount: float, base_currency: str, target_currency: str = "USD") -> float:
        if base_currency == target_currency:
            return amount
        
        pair = f"{target_currency}_{base_currency}" # Example format finding the multiplier
        # Wait, if converting EUR to USD, we need rate of EUR_USD. Say 1 EUR = 1.1 USD
        pair = f"{base_currency}_{target_currency}"
        
        rate = self.entry_handler.handle(pair)
        return amount * rate
