from dash import html, dcc
import utils

class DashChecklist:
    def __init__(self):
        self.id = "checklist-id"
        self.x_ma_val = "x_ma"
        self.rsi_val = "rsi"
        self.bb_val = "b_bands"

    def layout(self):
        _item_style = {"color": utils.colors["text_secondary"], "fontSize": "12px", "fontFamily": utils.font_mono, "textTransform": "uppercase"}

        return html.Div(
            children=[
                html.Div("▶ TECHNICAL INDICATORS", style={
                    "color": utils.colors["text"],
                    "fontSize": "15px",
                    "fontWeight": "700",
                    "letterSpacing": "2px",
                    "fontFamily": utils.font_mono,
                    "marginBottom": "8px",
                    "marginTop": "4px",
                }),
                dcc.Checklist(
                    id=self.id,
                    options=[
                        {
                            "label": html.Div(
                                ["Crossing MA"],
                                style=_item_style,
                            ),
                            "value": self.x_ma_val,
                        },
                        {
                            "label": html.Div(
                                ["Bollinger bands"],
                                style=_item_style,
                            ),
                            "value": self.bb_val,
                        },
                        {
                            "label": html.Div(
                                ["RSI"],
                                style=_item_style,
                            ),
                            "value": self.rsi_val,
                        },
                    ],
                    value=["x_ma"],
                    labelStyle={
                        "display": "flex",
                        "alignItems": "center",
                        "gap": "6px",
                        "padding": "3px 0",
                        "borderBottom": "1px dashed #1a0500",
                    },
                    inputStyle={
                        "accentColor": utils.colors["text"],
                        "width": "13px",
                        "height": "13px",
                        "cursor": "pointer",
                    },
                ),
            ]
        )
