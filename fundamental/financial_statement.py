from pydantic import BaseModel, PrivateAttr
from enum import Enum
import plotly.graph_objects as go
import numpy as np
import os

from .balance_sheet import BalanceSheet
from .cash_flow import CashFlow
from .income_statement import IncomeStatement
from utils.comm_interface import *

class Period(Enum):
    ANNUALLY = "annually"
    QUARLY = "quarly"

class FinancialStatement(BaseModel):
    balance_sheet: list[BalanceSheet] | None = []
    cash_flow: list[CashFlow] | None = []
    income_statement: list[IncomeStatement] | None = []

    _url: str = PrivateAttr(default= os.getenv("FUNDAMENTAL_URL", "http://fundamental:3000"))
    _data_fetcher: CommunicationInterface = PrivateAttr(default=None)

    async def fetch_financial_statement(self, stock: str):
        endpoint = self._url + "/" + stock + "/" + "history"
        response = await self._data_fetcher.get(endpoint)
        if response is not None:
            return response
        else:
            return None

    def show_balance_sheet(self) -> go.Figure | None:
        if len(self.balance_sheet) == 0:
            return None

        dates = [item.financial_facts.end_date for item in self.balance_sheet]
        assets = [item.current_assets - item.inventory for item in self.balance_sheet]
        inventory = [item.inventory for item in self.balance_sheet]
        assets_plus_inventory = [a + i for a, i in zip(assets, inventory)]
        liabilities = [item.current_liabilities for item in self.balance_sheet]

        total_assets = [item.total_assets for item in self.balance_sheet]
        total_liabilities = [item.total_liabilities for item in self.balance_sheet]

        hover_template = "%{y:$,.2f}"
        fig = go.Figure()
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
        fig.add_trace(
            go.Bar(
                x=dates,
                y=assets,
                marker_color="#99ef8f",
                hovertemplate=hover_template,
                name="Current assets",
                offsetgroup=0,
            ),
        )
        fig.add_trace(
            go.Bar(
                x=dates,
                y=inventory,
                marker_color="#88ace2",
                hovertemplate=hover_template,
                name="Inventory",
                offsetgroup=0,
                base=assets
            ),
        )
        fig.add_trace(
            go.Bar(
                x=dates,
                y=liabilities,
                marker_color="#f1ba8b",
                hovertemplate=hover_template,
                name="Current liabilities",
                offsetgroup=0,
                base=assets_plus_inventory
            ),
        )
        fig.add_trace(
            go.Bar(
                x=dates,
                y=total_assets,
                marker_color="#99ef8f",
                hovertemplate=hover_template,
                name="Total assets",
                offsetgroup=1
            ),
        )
        fig.add_trace(
            go.Bar(
                x=dates,
                y=total_liabilities,
                marker_color="#f1ba8b",
                hovertemplate=hover_template,
                name="Total liabilities",
                offsetgroup=1
            ),
        )
        fig.update_layout(
            template="plotly_dark",
            # 'relative' stacks positive values above 0 and negative below 0
            barmode="relative",
            title_text="Balance Sheet",
            yaxis_title="USD",
            bargroupgap=0.1,
            xaxis=dict(
                type="category",  # Treats the date as a label rather than a timeline
                tickformat="%Y-%m-%d",
            ),
        )
        return fig

    def show_income_statement(self) -> go.Figure | None:
        if len(self.income_statement) == 0:
            return None

        dates = [item.financial_facts.end_date for item in self.income_statement]
        cost_of_revenues = [item.cost_of_revenue for item in self.income_statement]
        operating_expenses = [item.operating_expense for item in self.income_statement]
        total_revenue = [item.total_revenue for item in self.income_statement]

        hover_template = "%{y:$,.2f}"
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=dates,
                y=cost_of_revenues,
                marker_color="#f1ba8b",
                hovertemplate=hover_template,
                name="Cost of Revenue",
                offsetgroup=0,
            )
        )
        fig.add_trace(
            go.Bar(
                x=dates,
                y=operating_expenses,
                marker_color="#88ace2",
                hovertemplate=hover_template,
                name="Operating Expenses",
                offsetgroup=0,
                base=cost_of_revenues,
            )
        )
        # --- Total revenue ---
        fig.add_trace(
            go.Bar(
                x=dates,
                y=total_revenue,
                marker_color="#c084fc",
                hovertemplate=hover_template,
                name="Total Revenue",
                offsetgroup=1,
            )
        )
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
        fig.update_layout(
            template="plotly_dark",
            # 'relative' stacks positive values above 0 and negative below 0
            barmode="relative",
            title_text="Income Statement",
            yaxis_title="USD",
            bargroupgap=0.1,
            xaxis=dict(
                type="category",  # Treats the date as a label rather than a timeline
                tickformat="%Y-%m-%d",
            ),
        )
        return fig

    def show_cash_flow(self) -> go.Figure | None:
        if len(self.cash_flow) == 0:
            return None

        dates = [item.financial_facts.end_date for item in self.cash_flow]
        end_cash_flow = [item.end_cash_flow_position for item in self.cash_flow]
        financing_cash_flow = [item.financing_cash_flow for item in self.cash_flow]
        investing_cash_flow = [item.investing_cash_flow for item in self.cash_flow]
        operating_cash_flow = [item.operating_cash_flow for item in self.cash_flow]

        hover_template = "%{y:$,.2f}"
        fig = go.Figure()
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=end_cash_flow,
                marker_color="#99ef8f",
                mode="lines+markers", # Ensure markers are visible
                marker=dict(
                    size=self._scale_sizes(end_cash_flow),
                    sizemode="diameter",
                    line=dict(width=1, color="white"),
                ),
                hovertemplate=hover_template,
                name="End cash flow",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=financing_cash_flow,
                marker_color="#8fefed",
                marker=dict(
                    size=self._scale_sizes(financing_cash_flow),
                    sizemode="diameter",
                    line=dict(width=1, color="white"),
                ),
                hovertemplate=hover_template,
                name="Financing cash flow",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=investing_cash_flow,
                marker=dict(
                    size=self._scale_sizes(financing_cash_flow),
                    sizemode="diameter",
                    line=dict(width=1, color="white"),
                ),
                marker_color="#e676b9",
                hovertemplate=hover_template,
                name="Investing cash flow",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=operating_cash_flow,
                marker_color="#ecda84",
                marker=dict(
                    size=self._scale_sizes(financing_cash_flow),
                    sizemode="diameter",
                    line=dict(width=1, color="white"),
                ),
                hovertemplate=hover_template,
                name="Operating cash flow",
            )
        )
        fig.update_layout(
            template="plotly_dark",
            # 'relative' stacks positive values above 0 and negative below 0
            barmode="relative",
            title_text="Cash Flow",
            yaxis_title="USD",
            bargroupgap=0.1,
            xaxis=dict(
                type="category",  # Treats the date as a label rather than a timeline
                tickformat="%Y-%m-%d",
            ),
        )
        return fig

    @staticmethod
    def _scale_sizes(nums, min_size=8, max_size=40):
        abs_vals = np.abs(nums)
        if abs_vals.max() == abs_vals.min():
            return [min_size] * len(nums)
        return [
            min_size + (v - abs_vals.min()) / (abs_vals.max() - abs_vals.min()) * (max_size - min_size)
            for v in abs_vals
        ]