from dash import dcc

class DashRSI:
    def __init__(self):
        self.rsi_graph_id = "rsi-graph"
    
    def layout(self):
        return dcc.Graph(
                    id=self.rsi_graph_id
                )