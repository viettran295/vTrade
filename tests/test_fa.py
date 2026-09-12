import polars as pl
from fundamental import FinancialStatement, BalanceSheet, IncomeStatement, IndustryRatios
from fundamental.common import FinancialFacts
from strategy import StrategyCrossingMA
from utils.comm_interface import HttpComm


def test_financial_statement_liquidity():
    fs = FinancialStatement(
        balance_sheet=[
            BalanceSheet(
                current_assets=1200000000,
                current_liabilities=600000000,
                inventory=150000000,
                total_assets=3000000000,
                total_liabilities=1500000000,
                total_equity=1500000000,
                financial_facts=FinancialFacts(end_date="2024-03-31", fiscal_period="Q1"),
            )
        ],
        income_statement=[
            IncomeStatement(
                total_revenue=2500000000,
                net_income=450000000,
                financial_facts=FinancialFacts(end_date="2024-03-31", fiscal_period="Q1"),
            )
        ],
        industry_ratios=IndustryRatios(
            current_ratio=1.45,
            quick_ratio=1.05,
            debt_to_equity_ratio=0.85,
        ),
    )

    # 1. Test Liquidity Ratios
    lr = fs.get_liquidity_ratios()
    assert lr["current_ratio"] == 2.0
    assert lr["quick_ratio"] == 1.75
    assert lr["peer_current_ratio"] == 1.45
    assert lr["peer_quick_ratio"] == 1.05

    # 2. Test Debt-to-Equity Gauge
    gauge = fs.show_debt_to_equity_gauge()
    assert gauge is not None
    assert len(gauge.data) > 0
    assert gauge.data[0].type == "indicator"
    assert gauge.data[0].value == 1.0  # 1500M liabilities / 1500M equity

    # 3. Test Quarterly Revenue Bars
    rev_bars = fs.show_quarterly_revenue_bars()
    assert rev_bars is not None
    assert len(rev_bars.data) == 2  # Revenue & Net Income traces
    assert rev_bars.data[0].name == "Revenue ($B)"
    assert rev_bars.data[1].name == "Net Income ($B)"

    # 4. Test Earnings Dates
    dates = fs.get_earnings_dates()
    assert "2024-03-31" in dates


def test_crossing_ma_with_bb_and_earnings_markers():
    strategy = StrategyCrossingMA(HttpComm)
    df_ma = pl.DataFrame({
        "datetime": ["2024-03-29", "2024-03-30", "2024-03-31", "2024-04-01"],
        "open": [100.0, 102.0, 101.0, 103.0],
        "high": [105.0, 106.0, 104.0, 107.0],
        "low": [99.0, 101.0, 100.0, 102.0],
        "close": [103.0, 105.0, 102.0, 106.0],
        "SMA_20": [101.0, 102.0, 103.0, 104.0],
        "SMA_50": [100.0, 100.5, 101.0, 101.5],
        "Sig_cross": [0, -1, 0, 1],
    })

    fig = strategy.show(df_ma)
    assert fig is not None
    trace_names = [t.name for t in fig.data]
    assert "Close price" in trace_names
    assert "SMA_20" in trace_names
    assert "SMA_50" in trace_names
    assert "Buying signal" in trace_names
    assert "Selling signal" in trace_names
