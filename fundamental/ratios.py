from pydantic import BaseModel, Field
from typing import Optional


class IndustryRatios(BaseModel):
    current_ratio: Optional[float] = 0.0
    debt_ratio: Optional[float] = 0.0
    debt_to_equity_ratio: Optional[float] = 0.0
    equity_ratio: Optional[float] = 0.0
    gross_profit_margin: Optional[float] = 0.0
    net_grofit_margin: Optional[float] = 0.0
    operating_grofit_margin: Optional[float] = 0.0
    quick_ratio: Optional[float] = 0.0
