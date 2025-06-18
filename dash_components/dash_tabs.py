from dash import html
import dash_bootstrap_components as dbc
from .dash_crossing_ma import DashCrossingMA
from .dash_rsi import DashRSI
from .dash_bb import DashBollingerBands

class DashTabs():
    def __init__(self):
        self.id_layout = "tabs-id"
        self.technical_analysis_id = "ta-id"
        self.paper_trading_id = "pt-id"

        self.x_ma = DashCrossingMA()
        self.rsi = DashRSI()
        self.bb = DashBollingerBands()

    def layout(self):
        return dbc.Tabs(
                    id=self.id_layout,
                    children=
                    [
                        dbc.Tab(
                            tab_id=self.technical_analysis_id,
                            label="Technical Analysis",
                            children=[
                                html.Br(),
                                self.x_ma.layout(),
                                html.Br(),
                                self.bb.layout(),
                                html.Br(),
                                self.rsi.layout(),
                                html.Br(),
                            ],
                            active_tab_style={
                                "fontStyle": "italic",
                            },
                            active_label_style={
                                "color": "#000000",
                            },
                            style={"marginBottom": "20px"},
                        ),
                        dbc.Tab(
                            tab_id=self.paper_trading_id,
                            label="Paper Trading",
                            children=[

                            ],
                            active_tab_style={
                                "fontStyle": "italic",
                            },
                            active_label_style={
                                "color": "#000000",
                            }
                        )
                    ]
                )
            