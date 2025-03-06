import polars as pl
from loguru import logger
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class BackTesting:
    
    fig = go.Figure()
    fig.update_layout(template="plotly_dark", xaxis_rangeslider_visible=False)

    datetime_col = "datetime"
    cash_col = "cash"
    number_shares_col = "nr_shares"
    profit_col = "profit"

    def __init__(self, init_cash: float = 10000):
        self.init_cash = init_cash
        self.cash = init_cash
        self.nr_shares = 0
        self.data = None
        self.order_size = []
        self.order_size_profit = []
        self.position = 1
        self.signal = "Signal"
        self.results = None
        
    def set_data(self, data: pl.DataFrame):
        if not any(col.startswith(self.signal) for col in data.columns):
            logger.error("Signal column is missing")
            return
        else:
            self.data = data
        
    def run(self, strategy: str):
        if self.data is None:
            logger.error("Data is missing")
            return

        self.__reset_attr()
        order_size = self.cash * 0.2
        datetime_data = []
        cash_data = []
        nr_shares_data = []
        profit_data = []

        for row in self.data.to_dicts():
            if row[strategy] == 1 and self.position == 1:
                self.position = 0
                shares_to_buy = order_size // row["close"]
                self.nr_shares += shares_to_buy
                self.cash -= shares_to_buy * row["close"]
            elif row[strategy] == 0 and self.position == 0:
                self.position = 1
                if self.nr_shares > 0:
                    shares_to_sell = self.nr_shares
                    self.nr_shares -= shares_to_sell
                    self.cash += shares_to_sell * row["close"]
            else:
                continue

            datetime_data.append(row["datetime"])
            cash_data.append(self.cash)
            nr_shares_data.append(self.nr_shares)
            profit_data.append(((self.cash - self.init_cash) / self.init_cash * 100))

        self.results = pl.DataFrame({
            self.datetime_col: datetime_data,
            self.cash_col: cash_data,
            self.number_shares_col: nr_shares_data,
            self.profit_col: profit_data
        })

    def report(self):
        logger.info("================ Report ====================")
        logger.info(f"Initial cash: {self.init_cash}")
        logger.info(f"Final cash: {self.cash}")
        logger.info(f"Amount buy: {self.amount_buy}")
        logger.info(f"Amount sell: {self.amount_sell}")
        logger.info(f"Number of shares: {self.nr_shares}")
        logger.info(f"Profit: {self.cash - self.init_cash}")
        logger.info(f"Percentage profit: {((self.cash - self.init_cash) / self.init_cash) * 100}%")
    
    def show_report(self, strategy: str) -> go.Figure:
        if self.results is None or self.results.is_empty():
            logger.warning(f"Strategy {strategy} no found.")
            return

        fig = make_subplots(rows=3, cols=1)
        fig.add_trace(go.Scatter(
                            x=self.results[self.datetime_col], 
                            y=self.results[self.profit_col],
                            mode="lines", name="Profit"
                        ),  row=1, col=1,
        )
        fig.add_hline(y=0, line_dash="dash", line_color="red", row=1, col=1)
        fig.add_trace(go.Scatter(
                            x=self.results[self.datetime_col], y=self.results[self.cash_col], 
                            mode="lines", name="Cash"
                        ),  row=2, col=1
        )
        fig.add_trace(go.Scatter(
                            x=self.results[self.datetime_col], y=self.results[self.number_shares_col], 
                            mode="lines", name="Shares"
                        ),  row=3, col=1
        )
        fig.update_layout(
                title={
                    "text": f"Backtesting report for {strategy}",
                    "x": 0.5
                },
                font=dict(size=18),
                template="plotly_dark", 
                xaxis_rangeslider_visible=False
        )

        return fig

    def order_size_over_profit(self):
        for order_size in range(10, self.init_cash, 10):
            tmp = []
            self.__reset_attr()
            signal_col = ''.join([col for col in self.data.columns if col.startswith(self.signal)])
            for row in self.data.to_dicts():
                if row[signal_col] == 1 and self.position == 1:
                    self.position = 0
                    shares_to_buy = order_size // row["close"]
                    self.nr_shares += shares_to_buy
                    self.cash -= shares_to_buy * row["close"]
                elif row[signal_col] == 0 and self.position == 0:
                    self.position = 1
                    if self.nr_shares > 0:
                        shares_to_sell = self.nr_shares
                        self.nr_shares -= shares_to_sell
                        self.cash += shares_to_sell * row["close"]
                else:
                    continue
                tmp.append(((self.cash - self.init_cash) / self.init_cash * 100))
            self.order_size.append(order_size)
            self.order_size_profit.append(max(tmp))

    def show_order_size_profit(self):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=self.order_size, y=self.order_size_profit, 
                                 mode="lines", name="Cash"))
        fig.update_layout(
            title="Order size and profit",
            xaxis_title="Order size ($)",
            yaxis_title="Profit (%)",
            template="plotly_dark", 
            xaxis_rangeslider_visible=False
        )
        fig.show()
    
    def __reset_attr(self):
        self.cash = self.init_cash
        self.nr_shares = 0