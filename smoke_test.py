"""
CI smoke test: runs the ExampleStrategy over generated candle data so the
workflow does not depend on a live exchange or on candles imported into the
database.

Usage:
    python smoke_test.py
"""
import numpy as np

from jesse.research import backtest, candles_from_close_prices

# Build a synthetic price series: an uptrend, then a downtrend, so the SMA
# crossover strategy enters both long and short positions.
prices = (
    list(np.linspace(30000, 36000, 500))   # uptrend
    + list(np.linspace(36000, 30000, 500)) # downtrend
)
trading_candles = candles_from_close_prices(prices)
warmup_candles = candles_from_close_prices(list(np.linspace(29000, 30000, 400)))

exchange = 'Binance Perpetual Futures'
symbol = 'BTC-USDT'
key = f'{exchange}-{symbol}'

candles = {key: {'exchange': exchange, 'symbol': symbol, 'candles': trading_candles}}
warmup = {key: {'exchange': exchange, 'symbol': symbol, 'candles': warmup_candles}}

backtest_config = {
    'starting_balance': 10_000,
    'fee': 0.04,
    'futures_leverage': 1,
    'futures_leverage_mode': 'cross',
    'type': 'futures',
    'exchange': exchange,
    'warm_up_candles': 200,
}

routes = [
    {
        'exchange': exchange,
        'symbol': symbol,
        'timeframe': '1m',
        'strategy': 'ExampleStrategy',
    }
]

result = backtest(
    config=backtest_config,
    routes=routes,
    data_routes=[],
    candles=candles,
    warmup_candles=warmup,
    generate_equity_curve=True,
)

metrics = result['metrics']
print('\n=== CI Smoke Test Results ===')
print(f"Strategy      : ExampleStrategy")
print(f"Symbol        : {symbol} (1m synthetic)")
print(f"Total trades  : {metrics['total']}")
print(f"Net profit    : {metrics['net_profit']:.2f}")
print(f"Sharpe ratio  : {metrics['sharpe_ratio']:.2f}")
print(f"Max drawdown  : {metrics['max_drawdown']:.2f}%")

assert metrics['total'] > 0, 'Expected at least one trade to be executed'
print('\nSMOKE TEST PASSED')