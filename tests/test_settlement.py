import unittest

from testudo.settlement import Policy, is_active, payout_per_share, settle, weekend_on_sale


def policy(**overrides) -> Policy:
    base = dict(spot_at_purchase=312.40, floor=0.10, shares=32.010243, purchased_at=0, expiry=7 * 86400, start_delay=4 * 3600)
    base.update(overrides)
    return Policy(**base)


class SettlementTests(unittest.TestCase):
    def test_nothing_above_the_floor(self):
        # Floor is 10% under 312.40, so 281.16. A close above it pays nothing.
        self.assertEqual(payout_per_share(300, 281.16, 203.06), 0.0)

    def test_pays_the_gap_then_stops_at_the_cap(self):
        self.assertAlmostEqual(payout_per_share(250, 281.16, 203.06), 31.16, places=2)
        self.assertAlmostEqual(payout_per_share(100, 281.16, 203.06), 78.10, places=2)

    def test_ten_thousand_notional_caps_at_2500(self):
        # The chart on how.html: TSLA $10,000, floor −10%, max payout $2,500.
        paid = settle(policy(), close=100, now=8 * 86400, feed_updated_at=8 * 86400, max_feed_age=3600)
        self.assertAlmostEqual(paid, 2500, delta=0.5)

    def test_stale_feed_waits(self):
        with self.assertRaisesRegex(ValueError, "stale"):
            settle(policy(), close=200, now=8 * 86400, feed_updated_at=8 * 86400 - 7200, max_feed_age=3600)

    def test_not_due_yet(self):
        with self.assertRaisesRegex(ValueError, "expiry"):
            settle(policy(), close=200, now=86400, feed_updated_at=86400, max_feed_age=3600)

    def test_start_delay(self):
        p = policy()
        self.assertFalse(is_active(p, 3 * 3600))
        self.assertTrue(is_active(p, 5 * 3600))
        self.assertFalse(is_active(p, p.expiry + 1))

    def test_weekend_sales_stop_at_friday_close(self):
        friday = 1_700_000_000
        self.assertTrue(weekend_on_sale(friday - 1, friday))
        self.assertFalse(weekend_on_sale(friday, friday))


if __name__ == "__main__":
    unittest.main()
