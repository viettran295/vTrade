from pydantic import BaseModel
from typing import Optional

from .common import FinancialFacts


class BalanceSheet(BaseModel):
    current_assets: int = 0
    current_liabilities: int = 0
    inventory: int = 0
    total_assets: int = 0
    total_equity: int = 0
    total_liabilities: int = 0
    financial_facts: Optional[FinancialFacts] = None
