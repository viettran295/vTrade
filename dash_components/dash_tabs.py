from dash import html, dcc
import dash_bootstrap_components as dbc
from .dash_crossing_ma import DashCrossingMA
from .dash_rsi import DashRSI
from .dash_bb import DashBollingerBands

from .dash_balance_sheet import DashBalanceSheet
from .dash_cash_flow import DashCashFlow
from .dash_income_statement import DashIncomeStatement


class DashTabs:
    def __init__(self):
        self.id_layout = "tabs-id"
        self.technical_analysis_id = "ta-id"
        self.fundamental_analysis_id = "fa-id"

        self.x_ma = DashCrossingMA()
        self.rsi = DashRSI()
        self.bb = DashBollingerBands()

        self.balance_sheet = DashBalanceSheet()
        self.cash_flow = DashCashFlow()
        self.income_statement = DashIncomeStatement()

    def layout(self):
        # Common styles for both tabs
        tab_style = {
            "padding": "12px",
            "backgroundColor": "#222",  # Matching your Darkly theme
            "color": "white",
            "borderTopLeftRadius": "15px",  # The Curve
            "borderTopRightRadius": "15px",  # The Curve
            "border": "1px solid #444",
            "marginRight": "10px",  # Gap between tabs
        }
        tab_selected_style = {
            **tab_style,
            "borderTop": "3px solid #198754",  # Green accent line
            "fontStyle": "italic",
        }
        return dcc.Tabs(
            id=self.id_layout,
            children=[
                dcc.Tab(
                    id=self.technical_analysis_id,
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
                    selected_style=tab_selected_style,
                    style=tab_style,
                ),
                dcc.Tab(
                    id=self.fundamental_analysis_id,
                    label="Fundamental Analysis",
                    children=[
                        html.Br(),
                        self.balance_sheet.layout(),
                        html.Br(),
                        self.cash_flow.layout(),
                        html.Br(),
                        self.income_statement.layout(),
                    ],
                    selected_style=tab_selected_style,
                    style=tab_style,
                ),
            ],
        )
