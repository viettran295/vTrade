from dash import dcc, html
import dash_bootstrap_components as dbc
import utils

class DashBollingerBands:
    def __init__(self):
        self.bb_graph_id = "bb-graph"
        self.bestperf_button = "bb-bestperf-button"
        self.id_layout = "bb-layout"

    def layout(self):
        return html.Div(
            id=self.id_layout,
            children=[
                html.Div(
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
                    children=[
                        html.Span("■ BOLLINGER BANDS (20, 2σ)"),
                        dbc.Button(
                            id=self.bestperf_button,
                            children="Best performance",
                            n_clicks=0,
                            color="info",
                            outline=True,
                            style={"fontFamily": utils.font_mono, "fontSize": "10px", "padding": "2px 8px", "textTransform": "uppercase"},
                        ),
                    ],
                ),
                dcc.Graph(
                    id=self.bb_graph_id,
                    config={"displayModeBar": False},
                ),
            ],
            style={"backgroundColor": utils.colors["background"]},
        )
