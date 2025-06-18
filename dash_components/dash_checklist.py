from dash import html, dcc
import utils

class DashChecklist():
    def __init__(self):
        self.id = "checklist-id"
        self.x_ma_val = "x_ma"
        self.rsi_val = "rsi"
        self.bb_val = "b_bands"
    
    def layout(self):
        return html.Div(
                    children=[
                        html.H4("Technical indicators"),
                        dcc.Checklist(
                            id=self.id,
                            options=[
                                {
                                    'label': html.Div(['Crossing MA'], 
                                                    style={'color': utils.colors["text"], 'font-size': 20,}
                                            ),
                                    'value': self.x_ma_val,
                                        
                                },
                                {
                                    'label': html.Div(['Bollinger bands'], 
                                                    style={'color': utils.colors["text"], 'font-size': 20}
                                            ),
                                    'value': self.bb_val
                                },
                                {
                                    'label': html.Div(['RSI'], 
                                                    style={'color': utils.colors["text"], 'font-size': 20}
                                            ),
                                    'value': self.rsi_val
                                }
                            ],
                            value=['x_ma'],
                            labelStyle={"display": "flex", "align-items": "center",},
                        )
                    ]
                )                
                                                