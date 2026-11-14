"""Quote a shield from the command line.

    python -m testudo TSLA 10000 --floor 0.10 --term week
    python -m testudo NVDA 5000 --floor 0.15 --term weekend --balance 5000000
"""

import argparse

from testudo.market import ASSETS, TERMS
from testudo.pricing import quote
from testudo.tiers import tier_for


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Price a Testudo shield with the reference model.")
    parser.add_argument("symbol", choices=sorted(ASSETS))
    parser.add_argument("notional", type=float, help="position size in USDC")
    parser.add_argument("--floor", type=float, default=0.10, help="drop that starts the payout, e.g. 0.10")
    parser.add_argument("--term", choices=sorted(TERMS), default="week")
    parser.add_argument("--balance", type=float, default=0.0, help="$TSTD balance, for the holder discount")
    args = parser.parse_args(argv)

    rank = tier_for(args.balance)
    q = quote(args.symbol, args.notional, args.floor, args.term, rank.discount)
    money = lambda n: f"${n:,.2f}"
    print(f"{q.asset.sym}  {q.term.label}  floor -{args.floor:.0%}  {rank.name}")
    print(f"  spot         {money(q.spot)}")
    print(f"  floor / cap  {money(q.floor_price)} / {money(q.cap_price)}")
    print(f"  fair         {money(q.fair)}")
    print(f"  margin       {money(q.margin)}")
    print(f"  load         {money(q.load)}")
    print(f"  fee          {money(q.fee)}   burn {money(q.burn)}")
    print(f"  discount     {money(q.discount)}")
    print(f"  premium      {money(q.premium)}" + ("   (minimum)" if q.min_applied else ""))
    print(f"  max payout   {money(q.max_payout)}")
    print(f"  chance pays  {q.chance_pays:.1%}")


if __name__ == "__main__":
    main()
