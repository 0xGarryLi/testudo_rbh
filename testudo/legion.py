"""The pool on the other side of every shield.

Two tranches. The first-loss tranche, funded by $TSTD stakers, earns double weight
on the pool margin and absorbs payouts before the senior USDC tranche.
"""

from dataclasses import dataclass

from testudo.market import DEPTH, STRESS_DROP


@dataclass(frozen=True)
class Pool:
    first_loss: float
    senior: float

    @property
    def capital(self) -> float:
        return self.first_loss + self.senior


def margin_split(income: float, pool: Pool) -> tuple[float, float]:
    """Split pool income (margin + load). First-loss capital has 2× weight."""
    if income < 0:
        raise ValueError("income is what the pool earned, not a payout")
    weight_front = 2.0 * pool.first_loss
    weight_rear = pool.senior
    total = weight_front + weight_rear
    if total == 0:
        return 0.0, 0.0
    return income * weight_front / total, income * weight_rear / total


def absorb(payout: float, pool: Pool) -> tuple[Pool, float]:
    """Pay `payout` from the front rank first. Returns the pool left and any shortfall."""
    if payout < 0:
        raise ValueError("payout must be positive")
    from_front = min(pool.first_loss, payout)
    rest = payout - from_front
    from_rear = min(pool.senior, rest)
    shortfall = rest - from_rear
    return Pool(pool.first_loss - from_front, pool.senior - from_rear), shortfall


def stress_loss(notional: float, floor: float, drop: float = STRESS_DROP) -> float:
    """What one shield pays if the stock falls `drop` (default 30%) from the purchase price."""
    gap = min(max(drop - floor, 0.0), DEPTH)
    return notional * gap


def can_underwrite(pool: Pool, open_stress: float, new_notional: float, floor: float) -> bool:
    """Coverage limit: the pool must be able to pay a 30% drop on everything it has sold."""
    return open_stress + stress_loss(new_notional, floor) <= pool.capital
