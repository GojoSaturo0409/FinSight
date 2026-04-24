import csv
import json
import io
from typing import List, Dict, Any

class PlaidParser:
    """Parses raw Plaid JSON strings into structured dictionaries."""
    def __init__(self, raw_data: Any):
        self.raw_data = raw_data

    def parse(self) -> List[Dict[str, Any]]:
        if isinstance(self.raw_data, str):
            return json.loads(self.raw_data)
        elif isinstance(self.raw_data, list):
            return self.raw_data
        return []


class CSVParser:
    """Parses raw CSV string data into lists of dictionaries mapping row columns."""
    def __init__(self, raw_data: Any):
        self.raw_data = raw_data

    def parse(self) -> List[Dict[str, str]]:
        if isinstance(self.raw_data, bytes):
            self.raw_data = self.raw_data.decode("utf-8")
        if isinstance(self.raw_data, str):
            reader = csv.DictReader(io.StringIO(self.raw_data))
            return [row for row in reader]
        elif isinstance(self.raw_data, list):
            return self.raw_data
        return []


class ManualEntryParser:
    """Parses raw form inputs into validated entries."""
    def __init__(self, raw_data: Any):
        self.raw_data = raw_data

    def parse(self) -> List[Dict[str, Any]]:
        # Validate or parse raw form bytes if necessary
        if isinstance(self.raw_data, str):
            return json.loads(self.raw_data)
        elif isinstance(self.raw_data, list):
            return self.raw_data
        return []
