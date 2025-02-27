from dash import html, dcc

class DashBackTesting:
    def __init__(self):
        self.backtest_graph = "backtest-graph"
        self.id_layout = "backtest-layout"
    
    def layout(self):
        return html.Div(
                    id=self.id_layout,
                    children=dcc.Graph(
                                    id=self.backtest_graph,
                                ),
                    style={
                        "display": "none",
                        "justifyContent": "center",
                        "alignItems": "center" 
                    },
                )