from services.shared.database import SessionLocal
from services.shared.models import Transaction
from services.transaction_service.categorization.service import get_default_service

db = SessionLocal()
service = get_default_service()

tx_models = db.query(Transaction).filter(Transaction.category.in_(["Unknown", "Uncategorized", "Miscellaneous"])).all()

tx_dicts = []
for tm in tx_models:
    tx_dicts.append({
        "id": tm.id,
        "amount": tm.amount,
        "category": tm.category,
        "merchant": tm.merchant
    })

res = service.process_transactions(tx_dicts)

count = 0
for modified in res:
    for tm in tx_models:
        if tm.id == modified["id"] and tm.category != modified["category"]:
            tm.category = modified["category"]
            count += 1
db.commit()
print(f"Migrated {count} old mock transactions in the database!")
