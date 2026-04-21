"""
Seed script to pre-populate InvestmentCache with realistic static data.
Prevents burning Alpha Vantage's 25 daily API calls during development/demo.

Usage:
    python investments/seed_cache.py
"""
import sys
import os
import json
import datetime

# Add backend dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine, Base
from models import InvestmentCache

# Realistic mock data for demo symbols
SEED_DATA = [
    {
        "symbol": "SPY",
        "price": 523.40,
        "trend": "up",
        "daily_prices": {
            "2024-03-31": 523.40, "2024-03-28": 521.18, "2024-03-27": 519.05,
            "2024-03-26": 517.62, "2024-03-25": 519.98, "2024-03-22": 518.34,
            "2024-03-21": 520.12, "2024-03-20": 515.80, "2024-03-19": 514.25,
            "2024-03-18": 512.90, "2024-03-15": 510.60, "2024-03-14": 513.05,
            "2024-03-13": 512.41, "2024-03-12": 511.88, "2024-03-11": 509.75,
            "2024-03-08": 512.30, "2024-03-07": 510.10, "2024-03-06": 508.90,
            "2024-03-05": 507.20, "2024-03-04": 505.45, "2024-03-01": 508.10,
            "2024-02-29": 506.85, "2024-02-28": 505.30, "2024-02-27": 507.90,
            "2024-02-26": 504.65, "2024-02-23": 506.20, "2024-02-22": 503.80,
            "2024-02-21": 501.10, "2024-02-20": 499.50, "2024-02-16": 502.30,
        },
    },
    {
        "symbol": "BND",
        "price": 72.85,
        "trend": "up",
        "daily_prices": {
            "2024-03-31": 72.85, "2024-03-28": 72.70, "2024-03-27": 72.60,
            "2024-03-26": 72.50, "2024-03-25": 72.65, "2024-03-22": 72.55,
            "2024-03-21": 72.45, "2024-03-20": 72.30, "2024-03-19": 72.20,
            "2024-03-18": 72.15, "2024-03-15": 72.00, "2024-03-14": 72.10,
            "2024-03-13": 71.95, "2024-03-12": 71.85, "2024-03-11": 71.75,
            "2024-03-08": 71.90, "2024-03-07": 71.80, "2024-03-06": 71.70,
            "2024-03-05": 71.60, "2024-03-04": 71.50, "2024-03-01": 71.65,
            "2024-02-29": 71.55, "2024-02-28": 71.40, "2024-02-27": 71.50,
            "2024-02-26": 71.35, "2024-02-23": 71.45, "2024-02-22": 71.30,
            "2024-02-21": 71.20, "2024-02-20": 71.10, "2024-02-16": 71.25,
        },
    },
    {
        "symbol": "VTI",
        "price": 261.20,
        "trend": "up",
        "daily_prices": {
            "2024-03-31": 261.20, "2024-03-28": 259.80, "2024-03-27": 258.40,
            "2024-03-26": 257.10, "2024-03-25": 259.00, "2024-03-22": 257.60,
            "2024-03-21": 259.30, "2024-03-20": 255.90, "2024-03-19": 254.80,
            "2024-03-18": 253.50, "2024-03-15": 252.00, "2024-03-14": 254.10,
            "2024-03-13": 253.60, "2024-03-12": 252.90, "2024-03-11": 251.30,
            "2024-03-08": 253.80, "2024-03-07": 252.00, "2024-03-06": 250.80,
            "2024-03-05": 249.50, "2024-03-04": 248.00, "2024-03-01": 250.60,
            "2024-02-29": 249.40, "2024-02-28": 248.10, "2024-02-27": 250.00,
            "2024-02-26": 247.50, "2024-02-23": 249.00, "2024-02-22": 246.80,
            "2024-02-21": 245.10, "2024-02-20": 243.50, "2024-02-16": 246.00,
        },
    },
]


def seed_investment_cache():
    """Pre-populate the InvestmentCache table with static demo data."""
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        for entry in SEED_DATA:
            existing = db.query(InvestmentCache).filter(
                InvestmentCache.symbol == entry["symbol"]
            ).first()

            if existing:
                existing.price = entry["price"]
                existing.trend = entry["trend"]
                existing.daily_prices = json.dumps(entry["daily_prices"])
                existing.last_updated = datetime.datetime.utcnow()
                print(f"  Updated cache for {entry['symbol']}: ${entry['price']}")
            else:
                new_entry = InvestmentCache(
                    symbol=entry["symbol"],
                    price=entry["price"],
                    trend=entry["trend"],
                    daily_prices=json.dumps(entry["daily_prices"]),
                    last_updated=datetime.datetime.utcnow(),
                )
                db.add(new_entry)
                print(f"  Created cache for {entry['symbol']}: ${entry['price']}")

        db.commit()
        print("Investment cache seeded successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding InvestmentCache with demo data...")
    seed_investment_cache()
