from dash import dcc, html
import dash_bootstrap_components as dbc

class DashRSI:
    def __init__(self):
        self.rsi_graph_id = "rsi-graph"
        self.bestperf_button = "rsi-backtest-button"
        self.id_layout = "rsi-layout"
    
    def layout(self):
        return html.Div(
                    id=self.id_layout,
                    children=[
                        html.Div(
                            dbc.Button(
                                id=self.bestperf_button,
                                children="Best performance",
                                target="blank",
                                n_clicks=0,
                                color="info",
                                outline=True,
                                style={
                                    "marginRight": "30px",
                                },
                            ),

                        ),
                        dcc.Graph(
                            id=self.rsi_graph_id
                        )
                    ],
                )