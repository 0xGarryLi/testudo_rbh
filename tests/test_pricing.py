import unittest

from testudo.pricing import basket_quote, quote


class PricingTests(unittest.TestCase):
    def test_published_week_table(self):
        # how.html: TSLA · $10,000 · 1 week. Premiums are the rounded quote-demo figures.
        expected = {0.05: 180.0, 0.10: 49.0, 0.15: 8.60, 0.20: 1.0}
        chances = {0.05: 0.275, 0.10: 0.102, 0.15: 0.024, 0.20: 0.003}
        for floor, premium in expected.items():
            q = quote("TSLA", 10_000, floor, "week")
            self.assertAlmostEqual(q.premium, premium, delta=0.6)
            self.assertAlmostEqual(q.chance_pays, chances[floor], delta=0.004)

    def test_published_month_table(self):
        expected = {"SPY": 2.34, "AAPL": 37.0, "NVDA": 242.0, "TSLA": 363.0}
        for sym, premium in expected.items():
            q = quote(sym, 10_000, 0.10, "month")
            self.assertAlmostEqual(q.premium, premium, delta=max(0.6, premium * 0.015))

    def test_hundred_shields_match_the_pool_example(self):
        # how.html: 100 shields, TSLA $10,000, floor −10%, one week.
        q = quote("TSLA", 10_000, 0.10, "week")
        premiums = 100 * q.premium
        fee = 100 * q.fee
        income = 100 * (q.margin + q.load)
        self.assertAlmostEqual(premiums, 4925, delta=2)
        self.assertAlmostEqual(100 * q.fair, 3382, delta=2)
        self.assertAlmostEqual(fee, 528, delta=2)
        self.assertAlmostEqual(income, 1016, delta=2)
        self.assertAlmostEqual(100 * q.burn, 317, delta=2)
        self.assertAlmostEqual(100 * q.operations, 211, delta=2)

    def test_discount_never_touches_the_fair_cost(self):
        full = quote("TSLA", 10_000, 0.10, "week", discount=0.0)
        half = quote("TSLA", 10_000, 0.10, "week", discount=0.50)
        self.assertEqual(half.fair, full.fair)
        self.assertAlmostEqual(half.discount, -0.50 * (full.margin + full.load + full.fee))
        self.assertLess(half.premium, full.premium)
        self.assertGreater(half.premium, half.fair)

    def test_deep_floor_uses_the_one_dollar_minimum(self):
        q = quote("SPY", 1_000, 0.20, "weekend")
        self.assertTrue(q.min_applied)
        self.assertEqual(q.premium, 1.0)

    def test_closer_than_five_percent_is_not_sold(self):
        with self.assertRaises(ValueError):
            quote("TSLA", 10_000, 0.04, "week")

    def test_weekend_costs_more_than_the_same_clock_time_without_the_gap(self):
        weekend = quote("TSLA", 10_000, 0.10, "weekend")
        self.assertEqual(weekend.term.vol_mult, 1.35)
        self.assertGreater(weekend.fair, 0)

    def test_max_payout_is_a_quarter_of_notional(self):
        q = quote("NVDA", 8_000, 0.10, "month")
        self.assertAlmostEqual(q.max_payout, 2_000, places=6)

    def test_basket_splits_the_notional(self):
        parts = basket_quote(["AAPL", "MSFT", "SPY"], 9_000, 0.10, "month")
        alone = quote("AAPL", 3_000, 0.10, "month")
        self.assertEqual(len(parts), 3)
        self.assertAlmostEqual(parts[0].premium, alone.premium, places=6)
        self.assertAlmostEqual(sum(p.fair for p in parts), alone.fair + quote("MSFT", 3_000, 0.10, "month").fair + quote("SPY", 3_000, 0.10, "month").fair)


if __name__ == "__main__":
    unittest.main()
