from pydantic import BaseModel
from typing import Optional
import plotly.graph_objects as go

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

        hover_template = "%{y:$,.2f}"
        fig = go.Figure()
        fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)
        fig.add_trace(
            go.Bar(
                x=[self.financial_facts.end_date],
                y=[self.current_assets],
                marker_color=["#198754"],
                hovertemplate=hover_template,
                name="Current assets",
            ),
        )
        fig.add_trace(
            go.Bar(
                x=[self.financial_facts.end_date],
                y=[-self.current_liabilities],
                marker_color=["#ff7700"],
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
