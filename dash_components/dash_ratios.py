from dash import html, dcc
import utils

class DashFinancialRatios:
    def __init__(self):
        self.id_layout = "financial-ratios-layout"
        self.id_financial_ratios_graph = "financial-ratios-graph"

    def layout(self):
        return html.Div(
            id=self.id_layout,
            children=[
                html.Div("■ FINANCIAL RATIOS — P/E  P/B  EV/EBITDA  ROE  ROA", style={
                    "color": utils.colors["text"], "fontFamily": utils.font_mono, "fontSize": "10px",
                    "fontWeight": "700", "letterSpacing": "3px",
                    "padding": "4px 12px", "backgroundColor": "#0a0a0a",
                    "borderLeft": f"3px solid {utils.colors["text"]}",
                    "borderBottom": "1px solid #330f00", "marginBottom": "8px",
                }),
                dcc.Graph(
                    id=self.id_financial_ratios_graph,
                    config={"displayModeBar": False},
                ),
            ],
            style={"backgroundColor": utils.colors["background"]},
        )
