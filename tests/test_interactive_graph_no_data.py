import polars as pl
from strategy import StrategyCrossingMA, StrategyBollingerBands, StrategyRSI
from utils.comm_interface import HttpComm
from playwright.sync_api import expect

from .common import *


def test_show_no_data_figure_structure():
    strategy = StrategyCrossingMA(HttpComm)
    fig = strategy.show_no_data(stock="XYZ")

    assert fig is not None
    assert hasattr(fig, "layout")
    assert "CROSSING MOVING AVERAGE — NO DATA" in fig.layout.title.text

    # Verify annotation content
    assert len(fig.layout.annotations) > 0
    ann_text = fig.layout.annotations[0].text
    assert "NO DATA AVAILABLE" in ann_text
    assert "XYZ" in ann_text


def test_show_no_data_empty_stock():
    strategy = StrategyCrossingMA(HttpComm)
    fig = strategy.show_no_data(stock=None)

    assert fig is not None
    ann_text = fig.layout.annotations[0].text
    assert "NO DATA AVAILABLE" in ann_text
    assert "No security selected" in ann_text


def test_crossing_ma_show_fallback_on_none_or_empty():
    strategy = StrategyCrossingMA(HttpComm)

    # Test None df
    fig_none = strategy.show(None, stock="INVALID_TICKER")
    assert fig_none is not None
    assert "INVALID_TICKER" in fig_none.layout.annotations[0].text

    # Test empty DataFrame
    fig_empty = strategy.show(pl.DataFrame(), stock="EMPTY_TICKER")
    assert fig_empty is not None
    assert "EMPTY_TICKER" in fig_empty.layout.annotations[0].text

    # Test DataFrame with missing columns
    df_missing_cols = pl.DataFrame({"datetime": ["2024-01-01"], "close": [100.0]})
    fig_missing = strategy.show(df_missing_cols, stock="MISSING_COLS")
    assert fig_missing is not None
    assert "INSUFFICIENT DATA COLUMNS" in fig_missing.layout.annotations[0].text


def test_bollinger_bands_show_fallback():
    strategy_bb = StrategyBollingerBands(HttpComm)
    fig = strategy_bb.show(None, stock="TEST_BB")
    assert fig is not None
    assert "TEST_BB" in fig.layout.annotations[0].text
    assert "BOLLINGER BANDS — NO DATA" in fig.layout.title.text


def test_rsi_show_fallback():
    strategy_rsi = StrategyRSI(HttpComm)
    fig = strategy_rsi.show(pl.DataFrame(), stock="TEST_RSI")
    assert fig is not None
    assert "TEST_RSI" in fig.layout.annotations[0].text
    assert "RELATIVE STRENGTH INDEX (RSI) — NO DATA" in fig.layout.title.text
