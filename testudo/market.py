"""Reference market data and the shared pricing parameters from the quote demo."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Asset:
    sym: str
    name: str
    price: float
    vol: float


@dataclass(frozen=True)
class Term:
    key: str
    label: str
    days: float
    vol_mult: float
    note: str


# Same reference prices and volatilities as site/public/assets/js/pricing.js.
ASSETS = {
    "TSLA": Asset("TSLA", "Tesla", 312.40, 0.58),
    "NVDA": Asset("NVDA", "NVIDIA", 184.10, 0.48),
    "AAPL": Asset("AAPL", "Apple", 231.75, 0.26),
    "AMZN": Asset("AMZN", "Amazon", 219.30, 0.33),
    "MSFT": Asset("MSFT", "Microsoft", 498.20, 0.25),
    "SPY": Asset("SPY", "S&P 500 ETF", 662.90, 0.16),
    "COIN": Asset("COIN", "Coinbase", 318.60, 0.78),
    "HOOD": Asset("HOOD", "Robinhood", 121.40, 0.70),
}

TERMS = {
    "weekend": Term("weekend", "Weekend", 2.5, 1.35, "Fri close → Mon open"),
    "week": Term("week", "1 week", 7, 1.0, "7 days"),
    "month": Term("month", "1 month", 30, 1.0, "30 days"),
}

# depth: a shield pays at most this fraction of notional below the floor.
# pool_margin: Legion's edge on the fair cost.
# utilization * util_slope: load surcharge at the demo pool fill (42%).
# protocol_fee: charged on fair + margin + load. 0.12 / 1.12 of the premium is ~11%.
DEPTH = 0.25
POOL_MARGIN = 0.25
UTILIZATION = 0.42
UTIL_SLOPE = 0.12
PROTOCOL_FEE = 0.12
MIN_PREMIUM = 1.0
MIN_FLOOR = 0.05  # floors closer than −5% are not sold
STRESS_DROP = 0.30
BURN_SHARE = 0.60
