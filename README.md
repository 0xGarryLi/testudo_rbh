# Testudo

Your stocks. Under a shell.

Testudo sells a **Scutum**: a shield on a stock position. You keep the shares. If the price finishes below your floor, the shield pays the gap, up to a cap, from a pool called the **Legion**. Settlement comes from a price feed. There is no claims desk.

This repository is the reference model behind the quote demo on [testudotrade.com](https://testudotrade.com). It is plain Python, with no dependencies, and the tests check it against the numbers published on the site. Shields are not on sale yet. Nothing here is a deployed contract or an offer to insure a position.

X: [@Testudo_rbh](https://x.com/Testudo_rbh)

Chain, when the shields go live: Robinhood Chain (4663). The token is **$TSTD**.

## A Scutum

One policy names a stock, a notional, a floor, a cap and an expiry.

The floor is how far the price can fall before the shield pays. A floor of −10% on a $312.40 stock sits at $281.16. The payout per share is zero above that, then one dollar per dollar below it, and it stops at the cap. The cap is 25% of the position below the floor, so a $10,000 shield pays at most $2,500.

```
close ≥ floor            payout = 0
floor > close > cap      payout = (floor − close) × shares
close ≤ cap              payout = 25% of notional
```

Three terms:

| Term | Clock | Volatility |
| --- | --- | --- |
| Weekend Shield | Friday close → Monday open, 2.5 days | reference vol × 1.35, for the gap |
| 1 week | 7 days | reference vol |
| 1 month | 30 days | reference vol |

A Basket Shield splits the notional in equal weights across the symbols you pick. Floors closer than −5% are not sold: they pay so often that the premium approaches the payout.

## Pricing

A shield is a capped put spread. The fair cost is what the pool expects to pay on average.

```
fair     = shares × [ Put(floor) − Put(cap) ]     Black–Scholes, zero rates
margin   = 25% × fair                              the Legion's edge
load     = fair × utilization × 12%               rises as the pool fills; the demo pool is 42% full
fee      = 12% × (fair + margin + load)           protocol
discount = −tier% × (margin + load + fee)         $TSTD holders; never touches the fair cost
premium  = fair + margin + load + fee + discount  and at least $1
```

The fee is about 11% of the premium a Civis pays. 60% of the fee buys $TSTD and burns it. 40% funds oracles, keepers and development.

Reference book, TSLA at 58% vol, $10,000, one week:

| Floor | Chance it pays | Premium |
| --- | --- | --- |
| −5% | 27.5% | $180 |
| −10% | 10.2% | $49 |
| −15% | 2.4% | $8.60 |
| −20% | 0.3% | $1 minimum |

Same notional, floor −10%, one month: SPY at 16% vol is $2.34, AAPL at 26% is $37, NVDA at 48% is $242, TSLA at 58% is $363. `tests/test_pricing.py` locks these figures.

## Settlement

Week and month shields settle on the close of the last day. Weekend Shields settle on the first feed update after Monday's open. Anyone can trigger settlement once it is due.

If the feed is stale, or the price is missing, settlement waits. A shield also stays inactive for a few hours after purchase, and Weekend Shields stop selling at Friday's close, so a name that is already falling cannot be insured after the fact.

## The Legion

Liquidity providers deposit USDC into the senior tranche. $TSTD stakers stand in the first-loss tranche.

- Pool income (margin + load) is split by capital, and first-loss capital counts double.
- Payouts are paid by the first-loss tranche until it is used up, then by the senior tranche.
- A coverage limit stops new sales once a 30% drop in every covered stock, all at once, would ask the pool for more than it holds. Because of the cap, a 30% drop on a −10% floor pays 20% of notional, not 30%.

## Ranks

The discount applies to margin, load and fee. The fair cost stays whole, so the pool is never underpriced. These balances are the ones the quote demo uses. Live thresholds are published after launch.

| Rank | $TSTD | Off the fee stack |
| --- | --- | --- |
| Civis | 0 | 0% |
| Legionary | 1,000,000 | 15% |
| Centurion | 5,000,000 | 30% |
| Legatus | 20,000,000 | 50% |

## Try it

Python 3.11 or newer. No packages to install.

```bash
python -m unittest discover -s tests -v
python -m testudo TSLA 10000 --floor 0.10 --term week
python -m testudo NVDA 5000 --floor 0.15 --term weekend --balance 5000000
```

The second command prices a one-week Tesla shield on a $10,000 position with a −10% floor. The third prices a weekend NVIDIA shield with a Centurion discount.

| Module | What you can check |
| --- | --- |
| `testudo/pricing.py` | fair value, premium, burn, baskets, the $1 minimum |
| `testudo/settlement.py` | the payout shape, a stale oracle, the start delay, Friday's cutoff |
| `testudo/legion.py` | double-weight income, first-loss absorption, the 30% coverage limit |
| `testudo/tiers.py` | which rank a balance falls into |

## Status

The site, the quote demo and this model are what exists today. The Scutum contract, the Legion pool and oracle settlement are the next build, on a testnet first. Governance over covered stocks, coverage limits and the fee split opens with the Legion phase.
