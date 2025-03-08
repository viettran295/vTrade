from dash import html
import dash_bootstrap_components as dbc
from .dash_crossing_ma import DashCrossingMA
from .dash_backtesting import DashBackTesting
from .dash_rsi import DashRSI

class DashTabs():
    def __init__(self):
        self.id_layout = "tabs-id"
        self.technical_analysis_id = "ta-id"
        self.backtesting_id = "bt-id"
        self.paper_trading_id = "pt-id"

        self.x_ma = DashCrossingMA()
        self.rsi = DashRSI()
        self.dash_bt = DashBackTesting()

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
                                self.rsi.layout(),
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
                            tab_id=self.backtesting_id,
                            label="Backtesting", 
                            children=[
                                html.Br(),
                                self.dash_bt.layout_crossing_ma(),
                                html.Br(),
                                self.dash_bt.layout_rsi(),
                            ],
                            active_tab_style={
                                "fontStyle": "italic",
                            },
                            active_label_style={
                                "color": "#000000",
                            }
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
            