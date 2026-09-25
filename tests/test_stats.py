import unittest

from zkc import stats
from zkc.cipher import load


class TestStats(unittest.TestCase):
    def test_z340_period_bigrams(self):
        # 社区著名统计：Z340 周期 1 有 25 个重复双字母，周期 19 有 37 个
        z340 = load("z340").text
        self.assertEqual(stats.bigram_repeats(z340, 1), 25)
        self.assertEqual(stats.bigram_repeats(z340, 19), 37)
        profile = stats.period_profile(z340, range(1, 41))
        self.assertEqual(max(profile, key=profile.get), 19)

    def test_z340_period19_is_significant(self):
        z340 = load("z340").text
        t = stats.shuffle_test(z340, lambda s: stats.bigram_repeats(s, 19), trials=2000, seed=0)
        self.assertGreater(t["z"], 4)
        self.assertLess(t["p"], 0.001)

    def test_z13_pattern(self):
        z13 = load("z13").text
        self.assertEqual(stats.isomorph_pattern(z13), [1, 2, 3, 4, 5, 6, 5, 7, 5, 8, 3, 1, 7])
        self.assertEqual(stats.repeated_positions(z13),
                         {"A": [1, 12], "N": [3, 11], "0": [5, 7, 9], "M": [8, 13]})
        self.assertAlmostEqual(stats.multiplicity(z13), 8 / 13)

    def test_z32_repeats(self):
        z32 = load("z32").text
        self.assertEqual(stats.repeated_positions(z32),
                         {"C": [1, 26], "9": [2, 32], "O": [6, 14]})
        self.assertAlmostEqual(stats.multiplicity(z32), 29 / 32)

    def test_bigram_repeats_definition(self):
        self.assertEqual(stats.bigram_repeats("ABABAB"), 3)  # AB×3, BA×2 → 2 + 1
        self.assertEqual(stats.bigram_repeats("ABCDEF"), 0)


if __name__ == "__main__":
    unittest.main()
