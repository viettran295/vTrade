from pydantic import BaseModel

from .balance_sheet import BalanceSheet

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


class FinancialReport(BaseModel):
    balance_sheet: BalanceSheet
    # income_statement: IncomeStatement
    # cash_flow: CashFlow
