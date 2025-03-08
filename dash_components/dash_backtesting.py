from dash import html, dcc

class DashBackTesting:
    def __init__(self):
        self.x_ma_graph_id = "x-ma-backtest-graph"
        self.rsi_graph_id = "rsi-backtest-graph"
        self.id_layout = "backtest-layout"

    def layout_crossing_ma(self):
        return html.Div(
                    children=dcc.Graph(
                                    id=self.x_ma_graph_id,
                                    style={
                                        "display": "none"
                                    }
                                ),
                    style={
                        "display": "block",
                        "justifyContent": "center",
                        "alignItems": "center" 
                    },
                )
    
    def layout_rsi(self):
        return html.Div(
                    children=dcc.Graph(
                                    id=self.rsi_graph_id,
                                    style={
                                        "display": "none"
                                    }
                                ),
                    style={
                        "display": "block",
                        "justifyContent": "center",
                        "alignItems": "center" 
                    },
                )