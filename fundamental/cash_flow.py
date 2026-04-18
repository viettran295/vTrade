from pydantic import BaseModel
from typing import Optional

from .common import FinancialFacts

class CashFlow(BaseModel):
    end_cash_flow_position: int = 0
    financing_cash_flow: int = 0
    investing_cash_flow: int = 0
    operating_cash_flow: int = 0
    financial_facts: Optional[FinancialFacts] = None