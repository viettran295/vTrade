from dash import html, dcc
import utils
import dash_bootstrap_components as dbc

class DashCrossingMA():
    def __init__(self):
        self.short_ma_input = "short-ma-input"
        self.long_ma_input = "long-ma-input"
        self.ma_types = "ma-types"
        self.apply_crossing_ma_button = "apply-crossing-ma-button"
        self.backtest_button = "x-ma-backtest-button"
        self.state_show_bt = "Show backtesting"
        self.state_hide_bt = "Hide backtesting"
        self.crossing_ma_graph = "crossing-ma-graph"
        self.id_layout = "crossing-ma-layout"

    def layout(self):
        return html.Div(
                    id=self.id_layout,
                    children=[
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
                        html.Div(
                            children=[
                                html.Label(
                                    "Short moving average",
                                    style={
                                        "textAlign": "center",
                                        "color": utils.colors["text"],
                                        "justifyContent": "left",
                                        "marginRight": "6px",
                                        "width": "160px"
                                    },
                                ),
                                dcc.Input(
                                    id=self.short_ma_input,
                                    type='number',
                                    value=20,
                                    style={
                                        "textAlign": "center",
                                        "color": utils.colors["text"],
                                        "justifyContent": "left",
                                        "marginRight": "30px",
                                        "width": "90px"
                                    },
                                ),
                                html.Label(
                                    "Long moving average",
                                    style={
                                        "textAlign": "center",
                                        "color": utils.colors["text"],
                                        "justifyContent": "left",
                                        "marginRight": "6px",
                                        "width": "160px"
                                    },
                                ),
                                dcc.Input(
                                    id=self.long_ma_input,
                                    type='number',
                                    value=50,
                                    style={
                                        "textAlign": "center",
                                        "color": utils.colors["text"],
                                        "justifyContent": "left",
                                        "marginRight": "30px",
                                        "width": "90px"
                                    },
                                ),
                                dcc.RadioItems(
                                    ["SMA", "EWM"], value="SMA",
                                    id=self.ma_types,
                                    style={
                                        "textAlign": "center",
                                        "color": utils.colors["text"],
                                        "justifyContent": "left",
                                        "marginRight": "30px",
                                    },
                                ),
                                dbc.Button(
                                    id=self.apply_crossing_ma_button,
                                    children="Apply",
                                    target="blank",
                                    n_clicks=0,
                                    color="success",
                                    style={
                                        "marginRight": "30px",
                                    },
                                ),
                            ],
                            style={
                                "display": "flex",
                                "justifyContent": "center",
                                "alignItems": "center" 
                            },
                        ),
                        dcc.Graph(
                            id=self.crossing_ma_graph,
                        ),
                    ],
                    style={
                        "display": "none",
                        "justifyContent": "center",
                        "alignItems": "center" 
                    },
                )