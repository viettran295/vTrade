from dash import html, dcc

class DashCashFlow:
    def __init__(self):
        self.id_layout = "cash-flow-layout"
        self.id_cash_flow_graph = "cash-flow-graph"

    def layout(self):
        return html.Div(
            id=self.id_layout, children=[dcc.Graph(id=self.id_cash_flow_graph)]
        )

