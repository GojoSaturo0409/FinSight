from .interfaces import ITransactionSource
from .adapters import PlaidAdapter, CSVAdapter, ManualEntryAdapter
from typing import List, Dict, Any

class TransactionFactory:
    @staticmethod
    def create_parser(source_type: str, raw_data: Any) -> ITransactionSource:
        if source_type == "plaid":
            # Data should be list of plaid transaction dicts
            return PlaidAdapter(raw_data)
        elif source_type == "csv":
            # Data should be list of csv rows
            return CSVAdapter(raw_data)
        elif source_type == "manual":
            # Data should be a list of manual entry dicts
            return ManualEntryAdapter(raw_data)
        else:
            raise ValueError(f"Unknown transaction source type: {source_type}")
