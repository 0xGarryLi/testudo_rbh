"""Premium of a Scutum: a capped put spread, then margin, load, fee and tier discount.

fair     = shares × [ Put(floor) − Put(cap) ]     Black–Scholes, zero rates
margin   = 25% × fair
load     = fair × utilization × 12%
fee      = 12% × (fair + margin + load)
discount = −tier% × (margin + load + fee)         never touches the fair cost
premium  = fair + margin + load + fee + discount, and at least $1
"""

import math
from dataclasses import dataclass

from testudo.market import (
    ASSETS,
    DEPTH,
    MIN_FLOOR,
    MIN_PREMIUM,
    POOL_MARGIN,
    PROTOCOL_FEE,
    TERMS,
    UTIL_SLOPE,
    UTILIZATION,
    Asset,
    Term,
)


def norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def put(spot: float, strike: float, vol: float, years: float) -> float:
    """European put, zero rates and dividends."""
    if strike <= 0 or spot <= 0 or vol <= 0 or years <= 0:
        return 0.0
    v = vol * math.sqrt(years)
    d1 = (math.log(spot / strike) + 0.5 * v * v) / v
    d2 = d1 - v
    return strike * norm_cdf(-d2) - spot * norm_cdf(-d1)


@dataclass(frozen=True)
class Quote:
    asset: Asset
    term: Term
    spot: float
    floor_price: float
    cap_price: float
    shares: float
    fair: float
    margin: float
    load: float
    fee: float
    discount: float
    premium: float
    max_payout: float
    chance_pays: float
    min_applied: bool

    @property
    def burn(self) -> float:
        from testudo.market import BURN_SHARE
        return self.fee * BURN_SHARE

    @property
    def operations(self) -> float:
        from testudo.market import BURN_SHARE
        return self.fee * (1.0 - BURN_SHARE)


def quote(asset: str | Asset, notional: float, floor: float, term: str | Term, discount: float = 0.0) -> Quote:
    """Price one shield.

    `floor` is the drop that starts the payout: 0.10 means the floor sits 10% under spot.
    `discount` is the holder's tier rate, 0.15 for Legionary.
    """
    found = ASSETS[asset] if isinstance(asset, str) else asset
    period = TERMS[term] if isinstance(term, str) else term
    if notional <= 0:
        raise ValueError("notional must be positive")
    if not 0.0 <= discount <= 1.0:
        raise ValueError("discount must be between 0 and 1")
    if floor < MIN_FLOOR or floor >= 1.0:
        raise ValueError(f"floor must be between {MIN_FLOOR:.0%} and 100%")

    spot = found.price
    years = period.days / 365.0
    vol = found.vol * period.vol_mult
    floor_price = spot * (1.0 - floor)
    cap_price = max(floor_price - DEPTH * spot, 0.01)
    shares = notional / spot
    fair = max(put(spot, floor_price, vol, years) - put(spot, cap_price, vol, years), 0.0) * shares
    margin = fair * POOL_MARGIN
    load = fair * UTILIZATION * UTIL_SLOPE
    fee = (fair + margin + load) * PROTOCOL_FEE
    disc = -(margin + load + fee) * discount
    total = fair + margin + load + fee + disc
    min_applied = total < MIN_PREMIUM
    if min_applied:
        total = MIN_PREMIUM
    v = vol * math.sqrt(years)
    chance = norm_cdf((math.log(floor_price / spot) + 0.5 * v * v) / v)
    return Quote(
        asset=found,
        term=period,
        spot=spot,
        floor_price=floor_price,
        cap_price=cap_price,
        shares=shares,
        fair=fair,
        margin=margin,
        load=load,
        fee=fee,
        discount=disc,
        premium=total,
        max_payout=(floor_price - cap_price) * shares,
        chance_pays=chance,
        min_applied=min_applied,
    )


def basket_quote(symbols: list[str], notional: float, floor: float, term: str, discount: float = 0.0) -> list[Quote]:
    """Equal-weight Basket Shield: the notional is split across the symbols."""
    if len(symbols) < 2:
        raise ValueError("a basket needs at least two symbols")
    each = notional / len(symbols)
    return [quote(sym, each, floor, term, discount) for sym in symbols]
