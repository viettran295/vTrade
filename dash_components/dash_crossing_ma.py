from dash import html, dcc
import utils
import dash_bootstrap_components as dbc


_label_style = {
    "textAlign": "center",
    "color": utils.colors["text"],
    "fontFamily": utils.font_mono,
    "fontSize": "11px",
    "fontWeight": "700",
    "letterSpacing": "1px",
    "marginRight": "6px",
    "width": "150px",
    "textTransform": "uppercase",
}

_input_style = {
    "textAlign": "center",
    "color": utils.colors["text"],
    "fontFamily": utils.font_mono,
    "fontSize": "13px",
    "backgroundColor": "#0a0a0a",
    "border": f"1px solid {utils.colors["text"]}",
    "borderRadius": "0",
    "marginRight": "24px",
    "width": "80px",
}

_radio_style = {
    "color": utils.colors["text"],
    "fontFamily": utils.font_mono,
    "fontSize": "12px",
    "letterSpacing": "1px",
    "marginRight": "24px",
}


class DashCrossingMA:
    def __init__(self):
        self.short_ma_input = "short-ma-input"
        self.long_ma_input = "long-ma-input"
        self.ma_types = "ma-types"
        self.apply_crossing_ma_button = "apply-crossing-ma-button"
        self.bestperf_button = "x-ma-bestperf-button"
        self.crossing_ma_graph = "crossing-ma-graph"
        self.id_layout = "crossing-ma-layout"

    def layout(self):
        return html.Div(
            id=self.id_layout,
            children=[
                # Section header bar
                html.Div(
                    "■ CROSSING MOVING AVERAGE",
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
                    }
                ),
                # Controls row
                html.Div(
                    children=[
                        dbc.Button(
                            id=self.bestperf_button,
                            children="Best performance",
                            n_clicks=0,
                            color="info",
                            outline=True,
                            style={
                                "marginRight": "20px",
                                "fontFamily": utils.font_mono,
                                "fontSize": "11px",
                                "textTransform": "uppercase",
                            },
                        ),
                        html.Label("Short moving average", style=_label_style),
                        dcc.Input(
                            id=self.short_ma_input,
                            type="number",
                            value=20,
                            style=_input_style,
                        ),
                        html.Label("Long moving average", style=_label_style),
                        dcc.Input(
                            id=self.long_ma_input,
                            type="number",
                            value=50,
                            style=_input_style,
                        ),
                        dcc.RadioItems(
                            ["SMA", "EWMA"],
                            value="SMA",
                            id=self.ma_types,
                            style=_radio_style,
                            inputStyle={
                                "accentColor": utils.colors["text"],
                                "marginRight": "4px",
                            },
                            labelStyle={
                                "marginRight": "12px",
                                "fontFamily": utils.font_mono,
                                "fontSize": "12px",
                                "color": utils.colors["text"],
                            },
                        ),
                        dbc.Button(
                            id=self.apply_crossing_ma_button,
                            children="Apply",
                            n_clicks=0,
                            color="success",
                            style={"fontFamily": utils.font_mono, "fontSize": "11px", "textTransform": "uppercase"},
                        ),
                    ],
                    style={
                        "display": "flex",
                        "justifyContent": "center",
                        "alignItems": "center",
                        "padding": "4px 12px 8px",
                    },
                ),
                dcc.Graph(
                    id=self.crossing_ma_graph,
                    config={"displayModeBar": False},
                ),
            ],
            style={
                "display": "none",
                "backgroundColor": utils.colors["background"],
            },
        )
