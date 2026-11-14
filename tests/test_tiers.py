import unittest

from testudo.tiers import tier_for


class TierTests(unittest.TestCase):
    def test_boundaries(self):
        self.assertEqual(tier_for(0).name, "Civis")
        self.assertEqual(tier_for(999_999).discount, 0.0)
        self.assertEqual(tier_for(1_000_000).name, "Legionary")
        self.assertEqual(tier_for(5_000_000).discount, 0.30)
        self.assertEqual(tier_for(20_000_000).name, "Legatus")
        self.assertEqual(tier_for(10**12).discount, 0.50)

    def test_negative_balance(self):
        with self.assertRaises(ValueError):
            tier_for(-1)


if __name__ == "__main__":
    unittest.main()
