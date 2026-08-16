"""
Programmatic backtest example using Jesse's research API.

Usage:
    python backtest_example.py

This does NOT require the web dashboard. It pulls 1m candles and runs
the ExampleStrategy over the given date range, printing the key metrics.

NOTE: candles passed to research.backtest() must always be 1-minute
candles. To trade another timeframe, set the timeframe in the route and
the framework resamples automatically.
"""
from datetime import datetime, timezone

import numpy as np

from jesse.research import backtest, get_candles


def to_ts(date_str: str) -> int:
    return int(datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc).timestamp() * 1000)


def main():
    # Candle data config
    exchange = 'Binance'
    symbol = 'BTC-USDT'
    route_timeframe = '1h'
    start_date = '2024-01-01'
    finish_date = '2024-03-01'

    # Always fetch 1m candles; the route timeframe is resampled internally
    trading_candles, warmup_candles = get_candles(
        exchange,
        symbol,
        '1m',
        to_ts(start_date),
        to_ts(finish_date),
        warmup_candles_num=200,
        caching=False,
    )

    key = f'{exchange}-{symbol}'
    candles = {
        key: {
            'exchange': exchange,
            'symbol': symbol,
            'candles': trading_candles,
        }
    }
    warmup = {
        key: {
            'exchange': exchange,
            'symbol': symbol,
            'candles': warmup_candles,
        }
    }

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
            'timeframe': route_timeframe,
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
    print('\n=== Backtest Results ===')
    print(f"Strategy      : ExampleStrategy")
    print(f"Symbol        : {symbol} ({route_timeframe})")
    print(f"Period        : {start_date} -> {finish_date}")
    print(f"Total trades  : {metrics['total']}")
    print(f"Win rate      : {metrics['win_rate']:.2f}%")
    print(f"Total return  : {metrics['total']:.2f}%")
    print(f"Sharpe ratio  : {metrics['sharpe_ratio']:.2f}")
    print(f"Max drawdown  : {metrics['max_drawdown']:.2f}%")


if __name__ == '__main__':
    main()