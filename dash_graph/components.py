from dash import html, dcc
import utils
import dash_bootstrap_components as dbc

class CrossingMA():
    def __init__(self):
        self.short_ma_input = "short_ma_input"
        self.long_ma_input = "long_ma_input"
        self.ma_types = "ma_types"
        self.apply_crossing_ma_button = "apply_crossing_ma_button"
        self.crossing_ma_graph = "crossing_ma_graph"
        self.id_layout = "crossing_ma_layout"

    def layout(self):
        return html.Div(
                    id=self.id_layout,
                    children=[
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