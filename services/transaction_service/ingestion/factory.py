from .interfaces import ITransactionSource
from .adapters import PlaidAdapter, CSVAdapter, ManualEntryAdapter
from typing import List, Dict, Any

class TransactionFactory:
    @staticmethod
    def create_parser(source_type: str, raw_data: Any) -> ITransactionSource:
        if source_type == "plaid":
            from .parsers import PlaidParser
            parsed_data = PlaidParser(raw_data).parse()
            return PlaidAdapter(parsed_data)
        elif source_type == "csv":
            from .parsers import CSVParser
            parsed_data = CSVParser(raw_data).parse()
            return CSVAdapter(parsed_data)
        elif source_type == "manual":
            from .parsers import ManualEntryParser
            parsed_data = ManualEntryParser(raw_data).parse()
            return ManualEntryAdapter(parsed_data)
        else:
            raise ValueError(f"Unknown transaction source type: {source_type}")
