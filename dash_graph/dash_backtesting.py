from dash import html, dcc

class DashBackTesting:
    def __init__(self):
        self.show_button = "show_button"
        self.backtest_graph = "backtest_graph"
        self.id_layout = "backtest_layout"
    
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