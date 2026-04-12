from pydantic import BaseModel
from typing import Optional

class FinancialFacts(BaseModel):
    accn: str = ""
    start_date: str = ""
    end_date: str = ""
    filed_date: str = ""
    fiscal_period: str = ""
    form_report: str = ""
    frame: str = ""

class BalanceSheet(BaseModel):
    current_assets: int = 0
    current_liabilities: int = 0
    inventory: int = 0
    total_assets: int = 0
    total_equity: int = 0
    total_liabilities: int = 0
    financial_facts: Optional[FinancialFacts] = None
