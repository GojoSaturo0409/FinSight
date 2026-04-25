from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    category = Column(String, index=True)
    merchant = Column(String, index=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)
    source = Column(String, index=True) # e.g., 'plaid', 'csv', 'manual'

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    category = Column(String, nullable=False, index=True)
    limit_amount = Column(Float, nullable=False, default=500.0)

class Investment(Base):
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)
    shares = Column(Float, nullable=False, default=0.0)
    average_price = Column(Float, nullable=False, default=0.0)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)

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
    daily_prices = Column(String) # JSON-encoded time series for chart rendering
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
