from dash import html, dcc
import utils


class DashFundamentalAnalysis:
    def __init__(self):
        self.id_layout = "fundamental-layout"
        self.current_ratio_val_id = "current-ratio-val"
        self.current_ratio_sub_id = "current-ratio-sub"
        self.quick_ratio_val_id = "quick-ratio-val"
        self.quick_ratio_sub_id = "quick-ratio-sub"
        self.gauge_graph_id = "debt-equity-gauge"
        self.revenue_graph_id = "quarterly-revenue-graph"

    def layout(self):
        return html.Div(
            id=self.id_layout,
            className="fa-fundamental-container",
            children=[
                # Header Bar
                html.Div(
                    className="fa-section-header",
                    children=[
                        html.Span("■ FUNDAMENTAL ANALYSIS", className="fa-header-title"),
                    ],
                ),

                # Section 1: Side-by-side Liquidity Ratios
                html.Div(
                    className="fa-liquidity-container",
                    children=[
                        html.Div(
                            className="fa-metric-card",
                            children=[
                                html.Div("CURRENT RATIO", className="fa-card-title"),
                                html.Div(id=self.current_ratio_val_id, className="fa-card-val", children="--"),
                                html.Div(id=self.current_ratio_sub_id, className="fa-card-sub", children="Peer Med: --"),
                            ],
                        ),
                        html.Div(
                            className="fa-metric-card",
                            children=[
                                html.Div("QUICK RATIO", className="fa-card-title"),
                                html.Div(id=self.quick_ratio_val_id, className="fa-card-val", children="--"),
                                html.Div(id=self.quick_ratio_sub_id, className="fa-card-sub", children="Peer Med: --"),
                            ],
                        ),
                    ],
                ),

                # Section 2: Debt-to-Equity Gauge vs Peer Medians
                html.Div(
                    className="fa-auge-container",
                    children=[
                        html.Div(
                            "■ DEBT-TO-EQUITY VS PEER MEDIAN",
                            className="fa-sub-header",
                        ),
                        dcc.Graph(
                            id=self.gauge_graph_id,
                            config={"displayModeBar": False},
                            style={"height": "190px"},
                        ),
                    ],
                ),

                # Section 3: Quarterly Revenue Bars
                html.Div(
                    className="fa-revenue-container",
                    children=[
                        html.Div(
                            "■ QUARTERLY REVENUE BARS",
                            className="fa-sub-header",
                        ),
                        dcc.Graph(
                            id=self.revenue_graph_id,
                            config={"displayModeBar": False},
                            style={"height": "220px"},
                        ),
                    ],
                ),
            ],
            style={"backgroundColor": utils.colors["background"]},
        )
