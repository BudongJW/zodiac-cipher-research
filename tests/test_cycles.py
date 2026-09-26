import math
import random
import unittest

from zkc.cipher import load, load_solution
from zkc.cycles import (canonical, cycle_loglik, homophone_prior, letter_sequences,
                        pattern_distribution, simulate, successor_consistency)


class TestCycles(unittest.TestCase):
    def test_canonical(self):
        self.assertEqual(canonical("xyxz"), (0, 1, 0, 2))

    def test_strict_cycle_simulation(self):
        seq = simulate(9, 3, 0.0, random.Random(1))
        self.assertEqual(canonical(seq), (0, 1, 2, 0, 1, 2, 0, 1, 2))

    def test_successor_consistency_strict(self):
        c, n = successor_consistency({"E": list("abcabcabc")})
        self.assertEqual((c, n), (1.0, 8))

    def test_pattern_distribution_strict(self):
        d = pattern_distribution(4, 2, 0.0)
        self.assertAlmostEqual(max(d["probs"].values()), 1.0, places=3)
        self.assertIn((0, 1, 0, 1), d["probs"])

    def test_z408_cycles_stronger_than_random(self):
        seqs = letter_sequences(load("z408").text, load_solution("z408_plaintext.txt"))
        self.assertGreater(successor_consistency(seqs)[0], 0.7)

    def test_loglik_rejects_inconsistent(self):
        self.assertEqual(cycle_loglik("aa", "XY", 0.2), float("-inf"))

    def test_loglik_prefers_cycle(self):
        prior = {"E": [3], "T": [1]}
        good = cycle_loglik("abcab", "EEEEE", 0.2, prior)   # 严格循环
        bad = cycle_loglik("aabbc", "EEEEE", 0.2, prior)    # 连续重复
        self.assertGreater(good, bad)
        self.assertTrue(math.isfinite(bad))

    def test_prior(self):
        prior = homophone_prior()
        self.assertIn(6, prior["E"])
        self.assertEqual(prior["J"], [1, 2])


if __name__ == "__main__":
    unittest.main()
