import unittest

from testudo.legion import Pool, absorb, can_underwrite, margin_split, stress_loss


class LegionTests(unittest.TestCase):
    def test_first_loss_earns_double_weight(self):
        # Equal capital: the front rank takes 2/3 of the margin, the rear rank 1/3.
        front, rear = margin_split(900, Pool(first_loss=100, senior=100))
        self.assertAlmostEqual(front, 600)
        self.assertAlmostEqual(rear, 300)

    def test_losses_hit_the_front_rank_first(self):
        left, shortfall = absorb(150, Pool(first_loss=100, senior=500))
        self.assertEqual(left, Pool(0, 450))
        self.assertEqual(shortfall, 0)

    def test_shortfall_when_both_ranks_are_used_up(self):
        left, shortfall = absorb(800, Pool(first_loss=100, senior=500))
        self.assertEqual(left.capital, 0)
        self.assertEqual(shortfall, 200)

    def test_stress_loss_for_a_thirty_percent_drop(self):
        # Floor −10%, cap 25% wide. A 30% drop pays 20% of notional, not the whole 30%.
        self.assertAlmostEqual(stress_loss(10_000, floor=0.10), 2_000)
        # Floor already 30% away: a 30% drop only just touches it.
        self.assertAlmostEqual(stress_loss(10_000, floor=0.30), 0)

    def test_coverage_limit_stops_the_sale(self):
        pool = Pool(first_loss=1_000, senior=4_000)
        self.assertTrue(can_underwrite(pool, open_stress=3_000, new_notional=5_000, floor=0.10))
        # 5_000 more notional at −10% adds 1_000 of stress, and 4_500 + 1_000 exceeds 5_000.
        self.assertFalse(can_underwrite(pool, open_stress=4_500, new_notional=5_000, floor=0.10))


if __name__ == "__main__":
    unittest.main()
