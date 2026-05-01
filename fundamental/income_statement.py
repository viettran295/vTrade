
from pydantic import BaseModel
from typing import Optional

from .common import FinancialFacts

class IncomeStatement(BaseModel):
    cost_and_expense: int = 0
    cost_of_revenue: int = 0
    operating_expense: int = 0
    operating_income: int = 0
    total_revenue: int = 0
    financial_facts: Optional[FinancialFacts] = None