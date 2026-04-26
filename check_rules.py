from services.transaction_service.categorization.strategies import RuleBasedStrategy
strategy = RuleBasedStrategy()
tx = {"merchant": "United Airlines"}
print("merchant string is:", tx.get("merchant"))
res = strategy.categorize(tx)
print("Result of categorize:", res)
