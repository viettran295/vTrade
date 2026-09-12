from dash import html, dcc
import utils
from .dash_crossing_ma import DashCrossingMA
from .dash_rsi import DashRSI
from .dash_bb import DashBollingerBands

from .dash_balance_sheet import DashBalanceSheet
from .dash_income_statement import DashIncomeStatement
from .dash_ratios import DashFinancialRatios


class DashTabs:
    def __init__(self):
        self.id_layout = "tabs-id"
        self.technical_analysis_id = "ta-id"
        self.fundamental_analysis_id = "fa-id"

        self.x_ma = DashCrossingMA()
        self.rsi = DashRSI()
        self.bb = DashBollingerBands()

        self.balance_sheet = DashBalanceSheet()
        self.income_statement = DashIncomeStatement()
        self.financial_ratios = DashFinancialRatios()

    def layout(self):
        # Bloomberg terminal tab style — inactive
        tab_style = {
            "padding": "6px 20px",
            "backgroundColor": "#000000",
            "color": "#888888",
            "borderTopLeftRadius": "0px",
            "borderTopRightRadius": "0px",
            "border": "1px solid #330f00",
            "borderBottom": "none",
            "marginRight": "2px",
            "fontFamily": utils.font_mono,
            "fontSize": "15px",
            "fontWeight": "700",
            "letterSpacing": "2px",
            "textTransform": "uppercase",
        }
        # Bloomberg terminal tab style — selected (orange fill, black text)
        tab_selected_style = {
            **tab_style,
            "backgroundColor": utils.colors["text"],
            "color": "#000000",
            "border": f"1px solid {utils.colors["text"]}",
            "borderBottom": "none",
        }

        # Tab content divider style
        content_style = {
            "backgroundColor": utils.colors["background"],
            "borderTop": f"2px solid {utils.colors["text"]}",
            "padding": "0",
        }

        return dcc.Tabs(
            id=self.id_layout,
            colors={"border": "#330f00", "primary": utils.colors["text"], "background": "#000000"},
            children=[
                dcc.Tab(
                    id=self.technical_analysis_id,
                    label="Technical Analysis",
                    children=[
                        html.Div(style={"height": "6px", "backgroundColor": utils.colors["background"]}),
                        self.x_ma.layout(),
                        html.Div(style={
                            "height": "1px", "backgroundColor": "#330f00",
                            "margin": "8px 0",
                        }),
                        self.bb.layout(),
                        html.Div(style={
                            "height": "1px", "backgroundColor": "#330f00",
                            "margin": "8px 0",
                        }),
                        self.rsi.layout(),
                        html.Div(style={"height": "12px"}),
                    ],
                    selected_style=tab_selected_style,
                    style=tab_style,
                ),
                dcc.Tab(
                    id=self.fundamental_analysis_id,
                    label="Fundamental Analysis",
                    children=[
                        html.Div(style={"height": "6px", "backgroundColor": utils.colors["background"]}),
                        self.balance_sheet.layout(),
                        html.Div(style={
                            "height": "1px", "backgroundColor": "#330f00",
                            "margin": "8px 0",
                        }),
                        self.income_statement.layout(),
                        html.Div(style={
                            "height": "1px", "backgroundColor": "#330f00",
                            "margin": "8px 0",
                        }),
                        self.financial_ratios.layout(),
                        html.Div(style={"height": "12px"}),
                    ],
                    selected_style=tab_selected_style,
                    style=tab_style,
                ),
            ],
            style={"backgroundColor": utils.colors["background"]},
            content_style=content_style,
        )
