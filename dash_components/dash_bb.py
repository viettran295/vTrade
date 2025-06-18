from dash import dcc, html
import dash_bootstrap_components as dbc

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
                            id=self.bb_graph_id
                        )
                    ],
                )