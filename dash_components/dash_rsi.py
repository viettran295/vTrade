from dash import dcc, html
import dash_bootstrap_components as dbc

class DashRSI:
    def __init__(self):
        self.rsi_graph_id = "rsi-graph"
        self.backtest_button = "rsi-backtest-button"
        self.state_show_bt = "Show backtesting"
        self.state_hide_bt = "Hide backtesting"
        self.id_layout = "rsi-layout"
    
    def layout(self):
        return html.Div(
                    id=self.id_layout,
                    children=[
                        html.Div(
                            dbc.Button(
                                id=self.backtest_button,
                                children=self.state_show_bt,
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