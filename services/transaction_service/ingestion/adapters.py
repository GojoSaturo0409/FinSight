from .interfaces import ITransactionSource
from typing import List, Dict, Any
import datetime

class PlaidAdapter(ITransactionSource):
    def __init__(self, raw_data: Any):
        self.raw_data = raw_data

    def fetch_transactions(self) -> List[Dict[str, Any]]:
        normalized = []
        txs = self.raw_data.get('transactions', []) if isinstance(self.raw_data, dict) else self.raw_data
        accounts = self.raw_data.get('accounts', []) if isinstance(self.raw_data, dict) else []

        # 1. Map Balances as initial Income
        for acc in accounts:
            bal = acc.get("balances", {}).get("current", 0)
            if bal and bal > 0:
                normalized.append({
                    "id": str(acc.get("account_id", f"bal_{len(normalized)}")),
                    "amount": float(bal),
                    "currency": acc.get("balances", {}).get("iso_currency_code", "USD") or "USD",
                    "category": "Income",
                    "merchant": f"Starting Balance - {acc.get('name', 'Bank Account')}",
                    "date": datetime.datetime.utcnow(),
                    "source": "plaid_balance"
                })

        # 2. Map existing transactions
        for item in txs:
            normalized.append({
                "id": str(item.get("transaction_id", "")),
                "amount": float(item.get("amount", 0)),
                "currency": item.get("iso_currency_code", "USD"),
                "category": item.get("category", ["Unknown"])[0] if isinstance(item.get("category"), list) else "Unknown",
                "merchant": item.get("merchant_name", "Unknown"),
                "date": datetime.datetime.strptime(item.get("date", "2000-01-01"), "%Y-%m-%d"),
                "source": "plaid"
            })
        return normalized

class CSVAdapter(ITransactionSource):
    def __init__(self, raw_data: List[Dict[str, str]]):
        self.raw_data = raw_data

    def fetch_transactions(self) -> List[Dict[str, Any]]:
        # Map Flat CSV map to internal format
        normalized = []
        for idx, row in enumerate(self.raw_data):
            # Assumes CSV fields are: Date, Description, Amount, Currency
            normalized.append({
                "id": f"csv_{idx}",
                "amount": float(row.get("Amount", 0)),
                "currency": row.get("Currency", "USD"),
                "category": "Uncategorized", # Handled later by ML/Rules
                "merchant": row.get("Description", "Unknown"),
                "date": datetime.datetime.strptime(row.get("Date", "2000-01-01"), "%Y-%m-%d"),
                "source": "csv"
            })
        return normalized

class ManualEntryAdapter(ITransactionSource):
    """Adapter for manually entered transactions (separate from CSV)."""
    def __init__(self, raw_data: List[Dict[str, Any]]):
        self.raw_data = raw_data

    def fetch_transactions(self) -> List[Dict[str, Any]]:
        normalized = []
        for idx, entry in enumerate(self.raw_data):
            normalized.append({
                "id": f"manual_{idx}",
                "amount": float(entry.get("amount", 0)),
                "currency": entry.get("currency", "USD"),
                "category": entry.get("category", "Uncategorized"),
                "merchant": entry.get("merchant", "Unknown"),
                "date": datetime.datetime.strptime(
                    entry.get("date", "2000-01-01"), "%Y-%m-%d"
                ) if isinstance(entry.get("date"), str) else entry.get("date", datetime.datetime.utcnow()),
                "source": "manual"
            })
        return normalized
