"""Holder ranks. The discount comes off margin, load and fee, never off the fair cost.

The quote demo uses these reference balances. The site publishes the live thresholds
once the market has priced $TSTD.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Tier:
    name: str
    min_balance: int
    discount: float


TIERS = (
    Tier("Civis", 0, 0.0),
    Tier("Legionary", 1_000_000, 0.15),
    Tier("Centurion", 5_000_000, 0.30),
    Tier("Legatus", 20_000_000, 0.50),
)


def tier_for(balance: float) -> Tier:
    if balance < 0:
        raise ValueError("balance cannot be negative")
    current = TIERS[0]
    for rank in TIERS:
        if balance >= rank.min_balance:
            current = rank
    return current
