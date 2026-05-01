from dash import html, dcc


class DashBalanceSheet:
    def __init__(self):
        self.id_layout = "balance-sheet-layout"
        self.id_balance_sheet_graph = "balance-sheet-graph"

    def layout(self):
        return html.Div(
            id=self.id_layout, children=[dcc.Graph(id=self.id_balance_sheet_graph)]
        )
