from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
import os

# Add the backend dir to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion.router import router as ingestion_router
from categorization.router import router as categorization_router
from budget.router import router as budget_router
from recommendations.router import router as recommendations_router
from reports.router import router as reports_router
from auth.router import router as auth_router
from investments.router import router as investments_router
from currency_converter.router import router as currency_router


def _seed_demo_data():
    """Seed demo transactions and budgets if the DB is empty."""
    from database import SessionLocal
    import models
    from core.security import get_password_hash
    import datetime
    import uuid

    db = SessionLocal()
    try:
        # Create demo user if none exists
        user = db.query(models.User).first()
        if not user:
            user = models.User(
                email="demo@finsight.app",
                hashed_password=get_password_hash("demo123"),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Seed transactions if empty
        tx_count = db.query(models.Transaction).count()
        if tx_count == 0:
            demo_txs = [
                {"amount": 1500.00, "category": "Housing", "merchant": "Avalon Rent", "date": "2024-03-01", "source": "manual"},
                {"amount": 120.50, "category": "Food", "merchant": "Whole Foods", "date": "2024-03-03", "source": "manual"},
                {"amount": 45.00, "category": "Food", "merchant": "Chipotle", "date": "2024-03-05", "source": "manual"},
                {"amount": 15.99, "category": "Subscriptions", "merchant": "Netflix", "date": "2024-03-05", "source": "manual"},
                {"amount": 9.99, "category": "Subscriptions", "merchant": "Spotify", "date": "2024-03-05", "source": "manual"},
                {"amount": 2.99, "category": "Subscriptions", "merchant": "iCloud", "date": "2024-03-06", "source": "manual"},
                {"amount": 80.00, "category": "Transport", "merchant": "Uber", "date": "2024-03-07", "source": "manual"},
                {"amount": 35.00, "category": "Transport", "merchant": "Shell Gas", "date": "2024-03-08", "source": "manual"},
                {"amount": 200.00, "category": "Shopping", "merchant": "Amazon", "date": "2024-03-10", "source": "manual"},
                {"amount": 65.00, "category": "Food", "merchant": "DoorDash", "date": "2024-03-11", "source": "manual"},
                {"amount": 150.00, "category": "Utilities", "merchant": "Comcast Internet", "date": "2024-03-12", "source": "manual"},
                {"amount": 42.00, "category": "Entertainment", "merchant": "Cinema AMC", "date": "2024-03-14", "source": "manual"},
                {"amount": 85.00, "category": "Healthcare", "merchant": "CVS Pharmacy", "date": "2024-03-15", "source": "manual"},
                {"amount": 25.00, "category": "Food", "merchant": "Starbucks", "date": "2024-03-16", "source": "manual"},
                {"amount": 300.00, "category": "Education", "merchant": "Coursera", "date": "2024-03-18", "source": "manual"},
                {"amount": 55.00, "category": "Food", "merchant": "Dominos Pizza", "date": "2024-03-20", "source": "manual"},
                {"amount": 1500.00, "category": "Housing", "merchant": "Avalon Rent", "date": "2024-02-01", "source": "manual"},
                {"amount": 95.00, "category": "Food", "merchant": "Trader Joe's", "date": "2024-02-05", "source": "manual"},
                {"amount": 70.00, "category": "Transport", "merchant": "Lyft", "date": "2024-02-08", "source": "manual"},
                {"amount": 15.99, "category": "Subscriptions", "merchant": "Netflix", "date": "2024-02-05", "source": "manual"},
            ]
            for i, tx_data in enumerate(demo_txs):
                tx = models.Transaction(
                    id=str(uuid.uuid4()),
                    user_id=user.id,
                    amount=tx_data["amount"],
                    currency="USD",
                    category=tx_data["category"],
                    merchant=tx_data["merchant"],
                    date=datetime.datetime.strptime(tx_data["date"], "%Y-%m-%d"),
                    source=tx_data["source"],
                )
                db.add(tx)
            db.commit()

        # Seed budgets if empty
        budget_count = db.query(models.Budget).count()
        if budget_count == 0:
            default_budgets = [
                {"category": "Food", "limit_amount": 500},
                {"category": "Housing", "limit_amount": 2000},
                {"category": "Transport", "limit_amount": 300},
                {"category": "Subscriptions", "limit_amount": 100},
                {"category": "Shopping", "limit_amount": 400},
                {"category": "Utilities", "limit_amount": 200},
                {"category": "Entertainment", "limit_amount": 150},
                {"category": "Healthcare", "limit_amount": 200},
                {"category": "Education", "limit_amount": 500},
            ]
            for b in default_budgets:
                budget = models.Budget(
                    user_id=user.id,
                    category=b["category"],
                    limit_amount=b["limit_amount"],
                )
                db.add(budget)
            db.commit()

        # Seed investment cache
        inv_count = db.query(models.InvestmentCache).count()
        if inv_count == 0:
            import json
            seed_investments = [
                {"symbol": "SPY", "price": 523.40, "trend": "up",
                 "daily_prices": {"2024-03-31": 523.40, "2024-03-28": 521.18, "2024-03-27": 519.05,
                                  "2024-03-26": 517.62, "2024-03-25": 519.98, "2024-03-22": 518.34}},
                {"symbol": "BND", "price": 72.85, "trend": "up",
                 "daily_prices": {"2024-03-31": 72.85, "2024-03-28": 72.70, "2024-03-27": 72.60,
                                  "2024-03-26": 72.50, "2024-03-25": 72.65, "2024-03-22": 72.55}},
                {"symbol": "VTI", "price": 261.20, "trend": "up",
                 "daily_prices": {"2024-03-31": 261.20, "2024-03-28": 259.80, "2024-03-27": 258.40,
                                  "2024-03-26": 257.10, "2024-03-25": 259.00, "2024-03-22": 257.60}},
            ]
            import datetime as dt
            for inv in seed_investments:
                cache_entry = models.InvestmentCache(
                    symbol=inv["symbol"],
                    price=inv["price"],
                    trend=inv["trend"],
                    daily_prices=json.dumps(inv["daily_prices"]),
                    last_updated=dt.datetime.utcnow(),
                )
                db.add(cache_entry)
            db.commit()

    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables and seed demo data."""
    from database import create_tables
    create_tables()
    _seed_demo_data()
    yield


app = FastAPI(title="FinSight API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingestion_router, prefix="/ingestion", tags=["Ingestion"])
app.include_router(categorization_router, prefix="/categorization", tags=["Categorization"])
app.include_router(budget_router, prefix="/budget", tags=["Budget"])
app.include_router(recommendations_router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(reports_router, prefix="/reports", tags=["Reports"])
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(investments_router, prefix="/investments", tags=["Investments"])
app.include_router(currency_router, prefix="/currency", tags=["Currency"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FinSight API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
