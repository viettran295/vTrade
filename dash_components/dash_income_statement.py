from dash import html, dcc

class DashIncomeStatement:
    def __init__(self):
        self.id_layout = "income-statement-layout"
        self.id_cash_flow_graph = "income-statement-graph"

    def layout(self):
        return html.Div(
            id=self.id_layout, children=[dcc.Graph(id=self.id_cash_flow_graph)]
        )

