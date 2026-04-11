from pydantic import BaseModel, PrivateAttr
from enum import Enum
import plotly.graph_objects as go

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
    balance_sheet: list[BalanceSheet] | None = []
    income_statement: list[dict] | None = []
    cash_flow: list[dict] | None = []

    _url: str = PrivateAttr(default="http://localhost:3000")
    _data_fetcher: CommunicationInterface = PrivateAttr(default=None)

    async def fetch_financial_statement(self, stock: str):
        endpoint = self._url + "/" + stock + "/" + "history"
        response = await self._data_fetcher.get(endpoint)
        if response is not None:
            return response
        else:
            return None

    def show_current_ratio(self) -> go.Figure | None:
        if len(self.balance_sheet) == 0:
            return None

        dates = [item.financial_facts.end_date for item in self.balance_sheet]
        assets = [item.current_assets for item in self.balance_sheet]
        liabilities = [item.current_liabilities for item in self.balance_sheet]

        hover_template = "%{y:$,.2f}"
        fig = go.Figure()
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
        fig.add_trace(
            go.Bar(
                x=dates,
                y=assets,
                marker_color="#198754",
                hovertemplate=hover_template,
                name="Current assets",
            ),
        )
        fig.add_trace(
            go.Bar(
                x=dates,
                y=liabilities,
                marker_color="#ff7700",
                hovertemplate=hover_template,
                name="Current liabilities",
            ),
        )
        fig.update_layout(
            template="plotly_dark",
            # 'relative' stacks positive values above 0 and negative below 0
            barmode="relative",
            title_text="Balance Sheet Composition",
            yaxis_title="USD",
            xaxis=dict(
                type="category",  # Treats the date as a label rather than a timeline
                tickformat="%Y-%m-%d",
            ),
        )
        return fig
