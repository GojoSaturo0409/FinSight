import sys
import os

# Add backend dir to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.factory import TransactionFactory
from ingestion.adapters import PlaidAdapter, CSVAdapter
from budget.monitor import BudgetMonitor
from budget.observers import AlertObserver
from recommendations.chain import RecommendationChain
from core.security import create_access_token, verify_password, get_password_hash
from jose import jwt
from core.security import SECRET_KEY, ALGORITHM

class MockObserver(AlertObserver):
    def __init__(self):
        self.alerts = []
    def update(self, category, threshold, current_spend):
        self.alerts.append((category, threshold, current_spend))

def test_factory_pattern():
    data = [{"transaction_id": "1", "amount": 100, "iso_currency_code": "USD"}]
    parser = TransactionFactory.create_parser("plaid", data)
    assert isinstance(parser, PlaidAdapter)
    
    csv_data = [{"Amount": "50", "Currency": "USD"}]
    parser_csv = TransactionFactory.create_parser("csv", csv_data)
    assert isinstance(parser_csv, CSVAdapter)

def test_observer_pattern():
    monitor = BudgetMonitor()
    obs1 = MockObserver()
    obs2 = MockObserver()
    
    monitor.attach(obs1)
    monitor.attach(obs2)
    
    # 50 spend, limit 40 -> should trigger alert
    monitor.evaluate([{"category": "Food", "amount": 50}], {"Food": 40})
    
    assert len(obs1.alerts) == 1
    assert obs1.alerts[0] == ("Food", 40, 50)
    assert len(obs2.alerts) == 1

def test_chain_of_responsibility():
    chain = RecommendationChain()
    user_context = {"monthly_income": 1000, "monthly_spend": 900} 
    # High spend ratio -> should have 1 warning
    recs = chain.get_recommendations(user_context)
    assert len(recs) == 1
    assert "High Spend Warning" in recs[0]

def test_member_1_auth():
    # Test Password Hashing
    password = "secretpassword"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

    # Test JWT token creation and decoding
    token = create_access_token(data={"sub": "test@example.com"})
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload.get("sub") == "test@example.com"
    assert "exp" in payload

if __name__ == "__main__":
    print("Running Tests")
    test_factory_pattern()
    test_observer_pattern()
    test_chain_of_responsibility()
    test_member_1_auth()
    print("All unit tests passed successfully!")
