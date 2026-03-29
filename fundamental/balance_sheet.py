from pydantic import BaseModel
from typing import Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots


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

    def show_current_ratio(self) -> go.Figure | None:
        if self.current_assets <= 0 or self.current_liabilities <= 0:
            return None

        fig = make_subplots(rows=1, cols=2, subplot_titles=("Assets - Liabilities", ""))
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
        fig.add_trace(
            go.Bar(
                x=["Assets", "Liabilities"],
                y=[self.current_assets, self.current_liabilities],
                marker_color=["#198754", "#ff7700"],
            ),
            row=1,
            col=1,
        )
        return fig
