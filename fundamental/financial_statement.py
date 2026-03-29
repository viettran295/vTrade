from pydantic import BaseModel, PrivateAttr
from enum import Enum

from .balance_sheet import BalanceSheet
from utils.comm_interface import *


class Period(Enum):
    ANNUALLY = "annually"
    QUARLY = "quarly"


# class IncomeStatement(BaseModel):
#     cost_and_expenses: int
#     cost_of_revenue: int
#     operating_expense: int
#     operating_income: int
#     total_revenue: int
#     financial_facts: FinancialFacts


# class CashFlow(BaseModel):
#     end_cash_flow_position: int
#     financing_cash_flow: int
#     investing_cash_flow: int
#     operating_cash_flow: int
#     financial_facts: FinancialFacts


class FinancialStatement(BaseModel):
    balance_sheet: BalanceSheet | None = None
    # income_statement: IncomeStatement
    # cash_flow: CashFlow

    _url: str = PrivateAttr(default="http://localhost:3000")
    _data_fetcher: CommunicationInterface = PrivateAttr(default=None)

    async def fetch_financial_statement(
        self, stock: str, period: Period = Period.ANNUALLY
    ):
        endpoint = self._url + "/" + stock + "/" + period.value
        response = await self._data_fetcher.get(endpoint)
        if response is not None:
            return response
        else:
            return None
