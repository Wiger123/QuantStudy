import pandas as pd
import talib as ta
import numpy as np
import zipline
from zipline.api import symbol, record, order_target_percent, schedule_function
from zipline.utils.events import date_rules, time_rules

"""
简单双均线策略
"""


def initialize(context):
    print("init")
    context.asset = symbol('IBM')
    context.bar_window = 20
    schedule_function(rebalance, date_rules.every_day(), time_rules.market_open())


def rebalance(context, data):
    history = data.history(assets=context.asset,
                           fields=['close'],
                           bar_count=context.bar_window,
                           frequency='1d')
    date = history.index.values[-1]
    close = history['close'].values

    current_position = context.portfolio.positions[context.asset].amount
    current_price = data[context.asset].price
    record(price=current_price)
    print("持仓数==>%d" % current_position)

    short_value = ta.SMA(close, timeperiod=5)
    long_value = ta.SMA(close, timeperiod=10)

    buy_signal_triggered = False
    sell_signal_triggered = False

    if short_value[-1] >= long_value[-1] and short_value[-2] < long_value[-2]:
        buy_signal_triggered = True
    elif short_value[-1] <= long_value[-1] and short_value[-2] > long_value[-2]:
        sell_signal_triggered = True

    if buy_signal_triggered and current_position == 0:
        print(str(date) + '==>Buy')
        order_target_percent(context.asset, 1.0)

    elif sell_signal_triggered and current_position > 0:
        print(str(date) + '==>Sell')
        order_target_percent(context.asset, 0.0)
    else:
        print("No trading")


if __name__ == '__main__':
    start_session = pd.to_datetime('2013-01-01', utc=True)
    end_session = pd.to_datetime('2014-05-01', utc=True)
    bundle_name = "custom-csv-bundle"
    capital = 10000

    perf = zipline.run_algorithm(start=start_session,
                                 end=end_session,
                                 initialize=initialize,
                                 bundle=bundle_name,
                                 capital_base=capital)

    perf.to_pickle("output.pkl")
