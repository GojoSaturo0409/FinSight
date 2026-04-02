from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from database import Base
import datetime

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    category = Column(String, index=True)
    merchant = Column(String, index=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    source = Column(String, index=True) # e.g., 'plaid', 'csv', 'manual'

class ExchangeRateCache(Base):
    __tablename__ = "exchange_rate_cache"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    currency_pairs = Column(String, unique=True, index=True) # e.g., "USD_EUR"
    rate = Column(Float, nullable=False)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

class InvestmentCache(Base):
    __tablename__ = "investment_cache"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    symbol = Column(String, unique=True, index=True)
    price = Column(Float, nullable=False)
    trend = Column(String) # e.g., 'up', 'down'
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
