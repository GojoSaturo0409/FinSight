from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ITransactionSource(ABC):
    @abstractmethod
    def fetch_transactions(self) -> List[Dict[str, Any]]:
        pass
