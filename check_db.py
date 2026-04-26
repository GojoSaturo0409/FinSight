from services.shared.database import SessionLocal
from services.shared.models import Transaction, User
db = SessionLocal()
user = db.query(User).filter_by(email="test5@test.com").first()
if not user:
    print("User not found!")
else:
    txs = db.query(Transaction).filter_by(user_id=user.id).all()
    for t in txs:
        print(f"{t.merchant} -> {t.category}")
