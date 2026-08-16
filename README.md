# Jesse Trading Bot

A production-ready [Jesse](https://jesse.trade) trading project: a Python-based crypto
algorithmic trading framework with backtesting, optimization, Monte Carlo testing, and
paper/live trading — all managed through a web dashboard.

## Features

- **Web dashboard** on `:9000` (backtest, optimize, Monte Carlo, rule significance testing)
- **Example strategy** (`strategies/ExampleStrategy`) with hyperparameters + risk sizing
- **Docker Compose** for PostgreSQL + Redis (Jesse's required data stores)
- **Programmatic backtest** script (`backtest_example.py`) — no dashboard needed
- **GitHub Actions CI** — verifies imports + runs a smoke backtest on every push

## Project structure

```
.
├── strategies/            # Your trading strategies
│   └── ExampleStrategy/   # Working example (SMA crossover + trailing stop)
├── storage/               # Logs, trades, CSV, charts, optimize results
├── docker/                # docker-compose.yml (postgres + redis)
├── .env.example           # Configuration template
└── backtest_example.py    # Programmatic backtest example
```

## Quick start

### Option A — Docker (recommended, everything included)

```sh
cp .env.example .env
cd docker
docker-compose up
```

Open [http://localhost:9000](http://localhost:9000) (default password: `test`).

### Option B — Run Jesse directly on your machine

Requires Python 3.10+.

```sh
pip install jesse
cp .env.example .env
# point POSTGRES_HOST and REDIS_HOST to your local Postgres/Redis (see .env)
jesse run
```

## Backtesting a strategy (no dashboard)

```sh
pip install -r requirements.txt
python backtest_example.py
```

## Writing your own strategy

Create `strategies/MyStrategy/__init__.py`:

```python
from jesse.strategies import Strategy


class MyStrategy(Strategy):
    def should_long(self) -> bool:
        return True

    def should_short(self) -> bool:
        return False

    def should_cancel_entry(self) -> bool:
        return False

    def go_long(self):
        qty = self.balance / self.price
        self.buy = qty
        self.stop_loss = self.price * 0.98
        self.take_profit = self.price * 1.02

    def go_short(self):
        pass
```

Register it in the dashboard under **Routes**, or add it to a `routes` list in a
`research.backtest()` call.

## Notes

- `config.py` and `routes.py` at the project root are generated and managed by the
  web dashboard (they are gitignored on purpose).
- Live trading requires the separate `jesse_live` plugin and a license API token
  (set `LICENSE_API_TOKEN` in `.env`).
- License: MIT.