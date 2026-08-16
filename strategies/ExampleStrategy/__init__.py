from jesse.strategies import Strategy, cached
import jesse.indicators as ta
from jesse import utils


class ExampleStrategy(Strategy):
    # Hyperparameters (can be tuned with the optimizer)
    def hyperparameters(self):
        return [
            {'name': 'fast_period', 'type': int, 'min': 5, 'max': 50, 'default': 20},
            {'name': 'slow_period', 'type': int, 'min': 50, 'max': 200, 'default': 50},
            {'name': 'risk_per_trade', 'type': float, 'min': 0.5, 'max': 2.0, 'default': 1.0},
        ]

    @property
    def fast_period(self) -> int:
        return self.hp['fast_period']

    @property
    def slow_period(self) -> int:
        return self.hp['slow_period']

    @property
    def risk_per_trade(self) -> float:
        return self.hp['risk_per_trade']

    def should_long(self) -> bool:
        # Long when the fast SMA is above the slow SMA (uptrend)
        return ta.sma(self.candles, self.fast_period) > ta.sma(self.candles, self.slow_period)

    def should_short(self) -> bool:
        # Short when the fast SMA is below the slow SMA (downtrend)
        return ta.sma(self.candles, self.fast_period) < ta.sma(self.candles, self.slow_period)

    def should_cancel_entry(self) -> bool:
        # Cancel the pending entry if the trend flipped back
        return self.fast_period > self.slow_period and \
               ta.sma(self.candles, self.fast_period) == ta.sma(self.candles, self.slow_period)

    def go_long(self):
        # Enter with a market order sized by risk per trade
        entry = self.price
        stop = entry * 0.98
        qty = utils.risk_to_qty(self.balance, self.risk_per_trade / 100, entry, stop)
        self.buy = (qty, entry)
        self.stop_loss = (qty, stop)
        self.take_profit = (qty, entry * 1.04)

    def go_short(self):
        entry = self.price
        stop = entry * 1.02
        qty = utils.risk_to_qty(self.balance, self.risk_per_trade / 100, entry, stop)
        self.sell = (qty, entry)
        self.stop_loss = (qty, stop)
        self.take_profit = (qty, entry * 0.96)

    def update_position(self):
        # Trailing stop: lock in 50% of profit once the price moves 2% in our favor
        if self.is_long and self.position.pnl_percentage > 2:
            self.stop_loss = (self.position.qty, max(self.stop_loss[0][1], self.price * 0.99))
        if self.is_short and self.position.pnl_percentage > 2:
            self.stop_loss = (self.position.qty, min(self.stop_loss[0][1], self.price * 1.01))

    def on_open_position(self, order):
        pass

    def before_terminate(self):
        pass
