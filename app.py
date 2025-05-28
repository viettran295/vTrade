from dash import Dash, html, callback, Input, Output, State, dcc, ctx
import dash
import dash_bootstrap_components as dbc
import utils
from utils import DataFetch
from dash_components import RegisterCallbacks
from dotenv import load_dotenv
load_dotenv()

dbc_css = "https://cdn.jsdelivr.net/npm/bootswatch@4.5.2/dist/minty/bootstrap.min.css"

app = Dash(
    title="Trust the Algorithms",
    external_stylesheets=[dbc.themes.DARKLY, dbc_css, dbc.icons.FONT_AWESOME]
)
server = app.server
app._favicon = "bull_icon.ico"

rc = RegisterCallbacks()
fetcher = DataFetch()

app.layout = dbc.Container(
    style = {
        "backgroundColor": utils.colors["background"],
         "height": "100vh",
         "overflow": "hidden"
    },
    children = [
        dbc.Row(
            [                
                dbc.Col(
                    [
                        html.Div(
                            children=[
                                html.Img(src="assets/bull_icon.png"),
                            ],
                            style={
                                "display": "flex",
                                "justify-content": "right",
                            }
                        )
                    ],
                    width=5
                ),
                dbc.Col(
                    [
                        html.H1(
                            "Trust the Algorithms",
                            style={
                                "textAlign": "left",
                                "color": utils.colors["text"],
                            }
                        ),
                    ],
                    width=5
                )
            ],
        ),
        html.Br(),
        dbc.Row(
            [
                # Side Bar
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardHeader(
                                    html.H3("Configuration"),
                                    style={
                                        "backgroundColor": utils.colors["sidebar"],
                                    }
                                ),
                                dbc.CardBody(
                                    [
                                        dbc.Col(
                                            [
                                                html.Div(
                                                    [
                                                        dbc.Input(
                                                            id="search-stock",
                                                            type="text",
                                                            placeholder="Stock symbol",
                                                            className="mb-3 mr-3 ml-1 w-50"
                                                        ),
                                                        dbc.Button(
                                                            id="search-button",
                                                            children="Search",
                                                            target="blank",
                                                            n_clicks=0,
                                                            color="success",
                                                            className="mb-3"
                                                        ),
                                                    ],
                                                    style={
                                                        "display": "flex"
                                                    }
                                                ),
                                                rc.checklist.layout()
                                            ]
                                        )
                                    ],
                                    style={
                                        "display": "flex",
                                        "backgroundColor": utils.colors["sidebar"],
                                        "padding-left": "0px"
                                    }
                                ),
                            ], 
                        )
                    ],
                    width=2,
                ),
                # Main Content
                dbc.Col(
                    [
                        rc.tabs.layout()
                    ],
                    style={
                        "maxHeight": "900px",  # Set a max height
                        "overflowY": "auto",  # Enable vertical scrolling when needed
                    },
                )
            ],
            className="gx-0",
            style={
                "display": "flex"
            }
        ),
        dcc.Store(id="activate-search")
    ],
    fluid=True
)

@callback (
    Output("activate-search", "data"),
    Input("search-button", "n_clicks"),
    State("search-stock", "value"),
)
def update_stock_data(_, search_stock):
    if "search-button" == ctx.triggered_id:
        return search_stock
    return dash.no_update

rc.register_MA_plot_callbacks()
rc.register_RSI_plot_callback()
rc.register_best_performance_MA()

if __name__ == "__main__":
    app.run_server(debug=True)