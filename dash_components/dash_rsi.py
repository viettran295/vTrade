from dash import dcc, html
import dash_bootstrap_components as dbc
import utils

class DashRSI:
    def __init__(self):
        self.rsi_graph_id = "rsi-graph"
        self.bestperf_button = "rsi-bestperf-button"
        self.id_layout = "rsi-layout"

    def layout(self):
        return html.Div(
            id=self.id_layout,
            children=[
                html.Div(
                    children=[
                        html.Span("■ RSI — RELATIVE STRENGTH INDEX (14)"),
                        dbc.Button(
                            id=self.bestperf_button,
                            children="Best performance",
                            n_clicks=0,
                            color="info",
                            outline=True,
                            style={"fontFamily": utils.font_mono, "fontSize": "10px", "padding": "2px 8px", "textTransform": "uppercase"},
                        ),
                    ],
                    style={
                        "color": utils.colors["text"],
                        "fontFamily": utils.font_mono,
                        "fontSize": "10px",
                        "fontWeight": "700",
                        "letterSpacing": "3px",
                        "padding": "4px 12px",
                        "backgroundColor": "#0a0a0a",
                        "borderLeft": f"3px solid {utils.colors["text"]}",
                        "borderBottom": "1px solid #330f00",
                        "marginBottom": "8px",
                        "display": "flex",
                        "justifyContent": "space-between",
                        "alignItems": "center",
                    },
                ),
                dcc.Graph(
                    id=self.rsi_graph_id,
                    config={"displayModeBar": False},
                ),
            ],
            style={"backgroundColor": utils.colors["background"]},
        )
