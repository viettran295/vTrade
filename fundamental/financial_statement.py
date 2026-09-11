from pydantic import BaseModel, PrivateAttr
from enum import Enum
import plotly.graph_objects as go
import numpy as np
import os

from .balance_sheet import BalanceSheet
from .cash_flow import CashFlow
from .income_statement import IncomeStatement
from .ratios import IndustryRatios
from utils.comm_interface import *


PASTEL = {
    "mint": "#A8E6CF",  # Assets / Positive
    "blue": "#8EE0ED",  # Inventory / Secondary Assets
    "peach": "#FFD8BE",  # Liabilities / Costs
    "rose": "#FFB7B2",  # Expenses / Investing
    "lavender": "#D4B5FF",  # Revenue / Totals
    "yellow": "#FFF5BA",  # Operating Cash Flow
    "cyan": "#B2F7EF",  # Financing Cash Flow
    "orange": "#FFC09F",  # Industry Benchmark
}


class Period(Enum):
    ANNUALLY = "annually"
    QUARLY = "quarly"


class FinancialStatement(BaseModel):
    balance_sheet: list[BalanceSheet] | None = []
    cash_flow: list[CashFlow] | None = []
    income_statement: list[IncomeStatement] | None = []
    industry_ratios: IndustryRatios | None = None

    _url: str = PrivateAttr(
        default=os.getenv("FUNDAMENTAL_URL", "http://fundamental:8001")
    )
    _data_fetcher: CommunicationInterface = PrivateAttr(default=None)

    async def fetch_financial_statement(self, stock: str):
        endpoint = self._url + "/" + stock + "/" + "history"
        response = await self._data_fetcher.get(endpoint)
        if response is not None:
            return response
        else:
            return None

    async def fetch_industry_ratios(self, stock: str):
        endpoint = self._url + "/" + stock + "/" + "ratios"
        response = await self._data_fetcher.get(endpoint)
        if response is not None:
            return response
        else:
            return None

    def show_balance_sheet(self) -> go.Figure | None:
        has_balance_sheet = self.balance_sheet is not None and len(self.balance_sheet) > 0
        has_cash_flow = self.cash_flow is not None and len(self.cash_flow) > 0

        if not has_balance_sheet and not has_cash_flow:
            return None

        hover_template = "%{y:$,.2f}"
        fig = go.Figure()
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)

        if has_balance_sheet:
            dates = [item.financial_facts.end_date for item in self.balance_sheet]
            assets = [item.current_assets - item.inventory for item in self.balance_sheet]
            inventory = [item.inventory for item in self.balance_sheet]
            assets_plus_inventory = [a + i for a, i in zip(assets, inventory)]
            liabilities = [item.current_liabilities for item in self.balance_sheet]

            total_assets = [item.total_assets for item in self.balance_sheet]
            total_liabilities = [item.total_liabilities for item in self.balance_sheet]

            fig.add_trace(
                go.Bar(
                    x=dates,
                    y=assets,
                    marker_color=PASTEL["mint"],
                    hovertemplate=hover_template,
                    name="Current assets",
                    offsetgroup=0,
                ),
            )
            fig.add_trace(
                go.Bar(
                    x=dates,
                    y=inventory,
                    marker_color=PASTEL["blue"],
                    hovertemplate=hover_template,
                    name="Inventory",
                    offsetgroup=0,
                    base=assets,
                ),
            )
            fig.add_trace(
                go.Bar(
                    x=dates,
                    y=liabilities,
                    marker_color=PASTEL["peach"],
                    hovertemplate=hover_template,
                    name="Current liabilities",
                    offsetgroup=0,
                    base=assets_plus_inventory,
                ),
            )
            fig.add_trace(
                go.Bar(
                    x=dates,
                    y=total_assets,
                    marker_color=PASTEL["mint"],
                    hovertemplate=hover_template,
                    name="Total assets",
                    offsetgroup=1,
                ),
            )
            fig.add_trace(
                go.Bar(
                    x=dates,
                    y=total_liabilities,
                    marker_color=PASTEL["peach"],
                    hovertemplate=hover_template,
                    name="Total liabilities",
                    offsetgroup=1,
                ),
            )

        if has_cash_flow:
            cf_dates = [item.financial_facts.end_date for item in self.cash_flow]
            end_cash_flow = [item.end_cash_flow_position for item in self.cash_flow]
            financing_cash_flow = [item.financing_cash_flow for item in self.cash_flow]
            investing_cash_flow = [item.investing_cash_flow for item in self.cash_flow]
            operating_cash_flow = [item.operating_cash_flow for item in self.cash_flow]

            fig.add_trace(
                go.Scatter(
                    x=cf_dates,
                    y=end_cash_flow,
                    marker_color=PASTEL["mint"],
                    mode="lines+markers",
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
                    x=cf_dates,
                    y=financing_cash_flow,
                    marker_color=PASTEL["yellow"],
                    mode="lines+markers",
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
                    x=cf_dates,
                    y=investing_cash_flow,
                    mode="lines+markers",
                    marker=dict(
                        size=self._scale_sizes(investing_cash_flow),
                        sizemode="diameter",
                        line=dict(width=1, color="white"),
                    ),
                    marker_color=PASTEL["cyan"],
                    hovertemplate=hover_template,
                    name="Investing cash flow",
                )
            )
            fig.add_trace(
                go.Scatter(
                    x=cf_dates,
                    y=operating_cash_flow,
                    mode="lines+markers",
                    marker_color=PASTEL["rose"],
                    marker=dict(
                        size=self._scale_sizes(operating_cash_flow),
                        sizemode="diameter",
                        line=dict(width=1, color="white"),
                    ),
                    hovertemplate=hover_template,
                    name="Operating cash flow",
                )
            )

        title = (
            "Balance Sheet & Cash Flow"
            if (has_balance_sheet and has_cash_flow)
            else ("Balance Sheet" if has_balance_sheet else "Cash Flow")
        )

        fig.update_layout(
            template="plotly_dark",
            # 'relative' stacks positive values above 0 and negative below 0
            barmode="relative",
            title_text=title,
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
                marker_color=PASTEL["peach"],
                hovertemplate=hover_template,
                name="Cost of Revenue",
                offsetgroup=0,
            )
        )
        fig.add_trace(
            go.Bar(
                x=dates,
                y=operating_expenses,
                marker_color=PASTEL["rose"],
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
                marker_color=PASTEL["lavender"],
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
                marker_color=PASTEL["mint"],
                mode="lines+markers",  # Ensure markers are visible
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
                marker_color=PASTEL["yellow"],
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
                marker_color=PASTEL["cyan"],
                hovertemplate=hover_template,
                name="Investing cash flow",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=operating_cash_flow,
                marker_color=PASTEL["rose"],
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

    def show_financial_ratios(self) -> go.Figure | None:
        if not self.balance_sheet and not self.income_statement and not self.industry_ratios:
            return None

        # Build dates from balance_sheet (or income_statement if balance_sheet empty)
        bs_by_date = {
            item.financial_facts.end_date: item
            for item in (self.balance_sheet or [])
            if item.financial_facts and item.financial_facts.end_date
        }
        is_by_date = {
            item.financial_facts.end_date: item
            for item in (self.income_statement or [])
            if item.financial_facts and item.financial_facts.end_date
        }

        all_dates = sorted(list(set(list(bs_by_date.keys()) + list(is_by_date.keys()))), reverse=True)
        if not all_dates:
            # Fallback if no dates in statements but industry ratios exist
            categories = [
                "Current Ratio",
                "Quick Ratio",
                "Debt Ratio",
                "Equity Ratio",
                "Gross Margin",
                "Operating Margin",
                "Net Margin",
            ]
            fig = go.Figure()
            if self.industry_ratios:
                ind_vals = [
                    self.industry_ratios.current_ratio or 0.0,
                    self.industry_ratios.quick_ratio or 0.0,
                    self.industry_ratios.debt_ratio or 0.0,
                    self.industry_ratios.equity_ratio or 0.0,
                    self.industry_ratios.gross_profit_margin or 0.0,
                    self.industry_ratios.operating_grofit_margin or 0.0,
                    self.industry_ratios.net_grofit_margin or 0.0,
                ]
                fig.add_trace(
                    go.Bar(
                        x=categories,
                        y=ind_vals,
                        name="Industry Average",
                        marker_color=PASTEL["yellow"],
                    )
                )
            fig.update_layout(
                template="plotly_dark",
                title_text="Financial Ratios vs Industry Average",
                barmode="group",
            )
            return fig

        # Compute company ratios for each reporting period
        current_ratios = []
        quick_ratios = []
        debt_ratios = []
        equity_ratios = []
        gross_margins = []
        operating_margins = []
        net_margins = []

        for d in all_dates:
            bs = bs_by_date.get(d)
            inc = is_by_date.get(d)

            # Liquidity & Solvency from Balance Sheet
            cr = (
                (bs.current_assets / bs.current_liabilities)
                if (bs and bs.current_liabilities and bs.current_liabilities != 0)
                else 0.0
            )
            qr = (
                ((bs.current_assets - bs.inventory) / bs.current_liabilities)
                if (bs and bs.current_liabilities and bs.current_liabilities != 0)
                else 0.0
            )
            dr = (
                (bs.total_liabilities / bs.total_assets)
                if (bs and bs.total_assets and bs.total_assets != 0)
                else 0.0
            )
            er = (
                (bs.total_equity / bs.total_assets)
                if (bs and bs.total_assets and bs.total_assets != 0)
                else 0.0
            )

            # Profitability Margins from Income Statement
            gpm = 0.0
            opm = 0.0
            npm = 0.0
            if inc and inc.total_revenue and inc.total_revenue != 0:
                if inc.gross_profit:
                    gpm = inc.gross_profit / inc.total_revenue
                elif inc.cost_of_revenue:
                    gpm = (inc.total_revenue - inc.cost_of_revenue) / inc.total_revenue
                if inc.operating_income:
                    opm = inc.operating_income / inc.total_revenue
                if inc.net_income:
                    npm = inc.net_income / inc.total_revenue

            current_ratios.append(round(cr, 2))
            quick_ratios.append(round(qr, 2))
            debt_ratios.append(round(dr, 2))
            equity_ratios.append(round(er, 2))
            gross_margins.append(round(gpm, 2))
            operating_margins.append(round(opm, 2))
            net_margins.append(round(npm, 2))

        fig = go.Figure()

        # Company traces (bars or lines per metric across time)
        fig.add_trace(
            go.Bar(
                x=all_dates,
                y=current_ratios,
                name="Current Ratio",
                marker_color=PASTEL["mint"],
                offsetgroup=0,
            )
        )
        fig.add_trace(
            go.Bar(
                x=all_dates,
                y=quick_ratios,
                name="Quick Ratio",
                marker_color=PASTEL["blue"],
                offsetgroup=1,
            )
        )
        fig.add_trace(
            go.Bar(
                x=all_dates,
                y=debt_ratios,
                name="Debt Ratio",
                marker_color=PASTEL["peach"],
                offsetgroup=2,
            )
        )
        fig.add_trace(
            go.Bar(
                x=all_dates,
                y=equity_ratio if (equity_ratio := equity_ratios) else [],
                name="Equity Ratio",
                marker_color=PASTEL["rose"],
                offsetgroup=3,
            )
        )

        # Industry benchmarks as comparison reference lines / points
        if self.industry_ratios:
            ind = self.industry_ratios
            if ind.current_ratio is not None:
                fig.add_trace(
                    go.Scatter(
                        x=all_dates,
                        y=[round(ind.current_ratio, 2)] * len(all_dates),
                        name=f"Ind. Avg Current Ratio ({ind.current_ratio:.2f})",
                        mode="lines",
                        line=dict(color=PASTEL["mint"], dash="dash", width=1),
                    )
                )
            if ind.quick_ratio is not None:
                fig.add_trace(
                    go.Scatter(
                        x=all_dates,
                        y=[round(ind.quick_ratio, 2)] * len(all_dates),
                        name=f"Ind. Avg Quick Ratio ({ind.quick_ratio:.2f})",
                        mode="lines",
                        line=dict(color=PASTEL["blue"], dash="dash", width=1),
                    )
                )
            if ind.debt_ratio is not None:
                fig.add_trace(
                    go.Scatter(
                        x=all_dates,
                        y=[round(ind.debt_ratio, 2)] * len(all_dates),
                        name=f"Ind. Avg Debt Ratio ({ind.debt_ratio:.2f})",
                        mode="lines",
                        line=dict(color=PASTEL["peach"], dash="dash", width=1),
                    )
                )
            if ind.equity_ratio is not None:
                fig.add_trace(
                    go.Scatter(
                        x=all_dates,
                        y=[round(ind.equity_ratio, 2)] * len(all_dates),
                        name=f"Ind. Avg Equity Ratio ({ind.equity_ratio:.2f})",
                        mode="lines",
                        line=dict(color=PASTEL["rose"], dash="dash", width=1),
                    )
                )

        fig.update_layout(
            template="plotly_dark",
            title_text="Financial Ratios vs. Industry Average",
            yaxis_title="Ratio Value",
            barmode="group",
            bargroupgap=0.1,
            xaxis=dict(
                type="category",
                tickformat="%Y-%m-%d",
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.05,
                xanchor="left",
                x=0,
            ),
        )
        return fig

    @staticmethod
    def _scale_sizes(nums, min_size=8, max_size=40):
        abs_vals = np.abs(nums)
        if abs_vals.max() == abs_vals.min():
            return [min_size] * len(nums)
        return [
            min_size
            + (v - abs_vals.min())
            / (abs_vals.max() - abs_vals.min())
            * (max_size - min_size)
            for v in abs_vals
        ]

    def get_liquidity_ratios(self) -> dict:
        """Returns latest Current Ratio and Quick Ratio compared to peer median."""
        cr_company = None
        qr_company = None

        if self.balance_sheet and len(self.balance_sheet) > 0:
            # Sort or use latest item
            latest_bs = self.balance_sheet[0]
            if latest_bs.current_liabilities and latest_bs.current_liabilities != 0:
                cr_company = round(latest_bs.current_assets / latest_bs.current_liabilities, 2)
                qr_company = round((latest_bs.current_assets - latest_bs.inventory) / latest_bs.current_liabilities, 2)

        peer_cr = getattr(self.industry_ratios, "current_ratio", None) if self.industry_ratios else None
        peer_qr = getattr(self.industry_ratios, "quick_ratio", None) if self.industry_ratios else None

        return {
            "current_ratio": cr_company,
            "quick_ratio": qr_company,
            "peer_current_ratio": round(peer_cr, 2) if peer_cr is not None else None,
            "peer_quick_ratio": round(peer_qr, 2) if peer_qr is not None else None,
        }

    def get_earnings_dates(self) -> list[str]:
        """Returns unique sorted list of quarterly SEC filing / statement end dates."""
        dates = set()
        if self.income_statement:
            for item in self.income_statement:
                if item.financial_facts and item.financial_facts.end_date:
                    dates.add(item.financial_facts.end_date)
        if self.balance_sheet:
            for item in self.balance_sheet:
                if item.financial_facts and item.financial_facts.end_date:
                    dates.add(item.financial_facts.end_date)
        return sorted(list(dates))

    def show_debt_to_equity_gauge(self) -> go.Figure | None:
        """Generates a Bloomberg terminal-themed Debt-to-Equity gauge benchmarked against peer median."""
        company_de = 0.0
        if self.balance_sheet and len(self.balance_sheet) > 0:
            latest = self.balance_sheet[0]
            if latest.total_equity and latest.total_equity != 0:
                company_de = round(latest.total_liabilities / latest.total_equity, 2)
            elif latest.total_assets and latest.total_assets != 0:
                company_de = round(latest.total_liabilities / latest.total_assets, 2)

        peer_median = 1.0
        if self.industry_ratios:
            if self.industry_ratios.debt_to_equity_ratio:
                peer_median = round(self.industry_ratios.debt_to_equity_ratio, 2)
            elif self.industry_ratios.debt_ratio:
                peer_median = round(self.industry_ratios.debt_ratio, 2)

        max_val = max(3.0, round(max(company_de, peer_median) * 1.4, 1))

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=company_de,
                delta={
                    "reference": peer_median,
                    "position": "bottom",
                    "relative": False,
                    "valueformat": ".2f",
                    "font": {"color": "#ff9933", "size": 13, "family": "Courier Prime, Courier New, monospace"},
                },
                number={
                    "font": {"color": "#ff6600", "size": 28, "family": "Courier Prime, Courier New, monospace"},
                    "valueformat": ".2f",
                },
                gauge={
                    "axis": {
                        "range": [0, max_val],
                        "tickwidth": 1,
                        "tickcolor": "#ff6600",
                        "tickfont": {"color": "#888888", "size": 10, "family": "Courier Prime, monospace"},
                    },
                    "bar": {"color": "#ff6600", "thickness": 0.35},
                    "bgcolor": "#0a0a0a",
                    "borderwidth": 1,
                    "bordercolor": "#330f00",
                    "steps": [
                        {"range": [0, max_val * 0.33], "color": "rgba(0, 204, 68, 0.15)"},
                        {"range": [max_val * 0.33, max_val * 0.66], "color": "rgba(255, 153, 51, 0.15)"},
                        {"range": [max_val * 0.66, max_val], "color": "rgba(255, 51, 51, 0.15)"},
                    ],
                    "threshold": {
                        "line": {"color": "#00ccff", "width": 3},
                        "thickness": 0.85,
                        "value": peer_median,
                    },
                },
            )
        )

        fig.update_layout(
            paper_bgcolor="#050505",
            plot_bgcolor="#050505",
            font=dict(family="Courier Prime, Courier New, monospace", color="#e8e8e8"),
            margin=dict(l=25, r=25, t=10, b=10),
            height=180,
            annotations=[
                dict(
                    text=f"Peer Median: {peer_median:.2f} (Cyan Line)",
                    x=0.5,
                    y=0.0,
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    font=dict(color="#00ccff", size=10, family="Courier Prime, monospace"),
                )
            ],
        )
        return fig

    def show_quarterly_revenue_bars(self) -> go.Figure | None:
        """Generates a Bloomberg terminal-themed quarterly revenue bar chart."""
        if not self.income_statement:
            return None

        # Sort chronologically by date
        sorted_items = sorted(
            [item for item in self.income_statement if item.financial_facts and item.financial_facts.end_date],
            key=lambda x: x.financial_facts.end_date,
        )

        if not sorted_items:
            return None

        # Take last 8 quarters max for readability
        recent_items = sorted_items[-8:]
        dates = [
            f"{item.financial_facts.fiscal_period or ''} {item.financial_facts.end_date[-5:]}"
            if item.financial_facts.fiscal_period
            else item.financial_facts.end_date
            for item in recent_items
        ]
        revenues = [item.total_revenue / 1e9 if item.total_revenue else 0.0 for item in recent_items]
        net_incomes = [item.net_income / 1e9 if item.net_income else 0.0 for item in recent_items]

        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=dates,
                y=revenues,
                name="Revenue ($B)",
                marker_color="#ff6600",
                hovertemplate="%{x}<br>Revenue: $%{y:.2f}B<extra></extra>",
            )
        )
        fig.add_trace(
            go.Bar(
                x=dates,
                y=net_incomes,
                name="Net Income ($B)",
                marker_color="#00ccff",
                hovertemplate="%{x}<br>Net Income: $%{y:.2f}B<extra></extra>",
            )
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="#050505",
            plot_bgcolor="#050505",
            barmode="group",
            bargap=0.2,
            bargroupgap=0.1,
            margin=dict(l=35, r=10, t=10, b=25),
            height=210,
            xaxis=dict(
                tickfont=dict(color="#888888", size=9, family="Courier Prime, monospace"),
                gridcolor="#1a0a00",
            ),
            yaxis=dict(
                title=dict(text="$ Billions", font=dict(color="#888888", size=10)),
                tickfont=dict(color="#888888", size=9, family="Courier Prime, monospace"),
                gridcolor="#1a0a00",
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(color="#e8e8e8", size=9, family="Courier Prime, monospace"),
            ),
        )
        return fig


