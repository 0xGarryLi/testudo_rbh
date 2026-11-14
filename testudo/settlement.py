"""What a shield pays at expiry. No claims desk: the oracle price decides."""

from dataclasses import dataclass

from testudo.market import DEPTH


@dataclass(frozen=True)
class Policy:
    spot_at_purchase: float
    floor: float
    shares: float
    purchased_at: int
    expiry: int
    start_delay: int


def strikes(policy: Policy) -> tuple[float, float]:
    floor_price = policy.spot_at_purchase * (1.0 - policy.floor)
    cap_price = max(floor_price - DEPTH * policy.spot_at_purchase, 0.01)
    return floor_price, cap_price


def payout_per_share(close: float, floor_price: float, cap_price: float) -> float:
    """Zero above the floor, one-for-one below it, flat once the cap is reached."""
    return min(max(floor_price - close, 0.0), floor_price - cap_price)


def settle(policy: Policy, close: float, now: int, feed_updated_at: int, max_feed_age: int) -> float:
    """Return the USDC payout, or raise if settlement is not allowed yet."""
    if now < policy.expiry:
        raise ValueError("shield has not reached expiry")
    if now - feed_updated_at > max_feed_age:
        raise ValueError("oracle feed is stale; settlement waits")
    if close <= 0:
        raise ValueError("oracle price must be positive")
    floor_price, cap_price = strikes(policy)
    return payout_per_share(close, floor_price, cap_price) * policy.shares


def is_active(policy: Policy, now: int) -> bool:
    """Shields start a few hours after purchase, so a name already in free fall cannot be insured."""
    return policy.purchased_at + policy.start_delay <= now <= policy.expiry


def weekend_on_sale(now: int, friday_close: int) -> bool:
    """Weekend Shields stop selling at Friday's close."""
    return now < friday_close
