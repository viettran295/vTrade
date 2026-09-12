from dash import html, dcc
import utils

class DashBalanceSheet:
    def __init__(self):
        self.id_layout = "balance-sheet-layout"
        self.id_balance_sheet_graph = "balance-sheet-graph"

    def layout(self):
        return html.Div(
            id=self.id_layout,
            children=[
                html.Div("■ BALANCE SHEET — ASSETS / LIABILITIES / EQUITY", style={
                    "color": utils.colors["text"], "fontFamily": utils.font_mono, "fontSize": "10px",
                    "fontWeight": "700", "letterSpacing": "3px",
                    "padding": "4px 12px", "backgroundColor": "#0a0a0a",
                    "borderLeft": f"3px solid {utils.colors["text"]}",
                    "borderBottom": "1px solid #330f00", "marginBottom": "8px",
                }),
                dcc.Graph(
                    id=self.id_balance_sheet_graph,
                    config={"displayModeBar": False},
                ),
            ],
            style={"backgroundColor": utils.colors["background"]},
        )
