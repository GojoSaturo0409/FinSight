from services.transaction_service.categorization.service import get_default_service
service = get_default_service()
print("Current strategy:", service.current_strategy_name)
print("United Airlines:", service.categorize_single({"merchant": "United Airlines"}))
print("McDonald's:", service.categorize_single({"merchant": "McDonald's"}))
print("KFC:", service.categorize_single({"merchant": "KFC"}))
