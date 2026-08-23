from dash import html, dcc


class DashFinancialRatios:
    def __init__(self):
        self.id_layout = "financial-ratios-layout"
        self.id_financial_ratios_graph = "financial-ratios-graph"

    def layout(self):
        return html.Div(
            id=self.id_layout,
            children=[dcc.Graph(id=self.id_financial_ratios_graph)],
        )
