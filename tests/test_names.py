import unittest
from itertools import product

from zkc.cipher import load
from zkc.names import count_two_part_fits, fits


class TestNames(unittest.TestCase):
    z13 = load("z13").text

    def test_known_claims(self):
        # 见 references/attempts.md §3.2
        self.assertTrue(fits("DR EAT A TOTPEDO", self.z13))      # Garlick：符合
        self.assertFalse(fits("ALFRED E NEUMAN", self.z13))      # Bauer：两个 N 需解为 F 与 M
        self.assertFalse(fits("EARL VAN BEST JR", self.z13))     # Stewart：第 1、12 位不同
        self.assertFalse(fits("LAWRENCE KANE", self.z13))

    def test_simple_substitution_is_stricter(self):
        self.assertTrue(fits("ABCDEFEGEHCAG", self.z13, simple=True))
        self.assertTrue(fits("ABADEFEGEHAAG", self.z13))
        self.assertFalse(fits("ABADEFEGEHAAG", self.z13, simple=True))

    def test_two_part_count_matches_brute_force(self):
        first = {"DREAT": 1, "ALFRED": 2, "STEVE": 1, "GARY": 1, "EDDIE": 3}
        last = {"ATOTPEDO": 1, "ENEUMAN": 1, "PETEWEST": 2, "LYLELARGE": 1, "PENERDEN": 1}
        result = count_two_part_fits(self.z13, first, last)
        brute = [f + l for f, l in product(first, last) if len(f + l) == 13 and fits(f + l, self.z13)]
        self.assertEqual(result["fits"], len(brute))
        self.assertIn("DREAT ATOTPEDO", result["examples"])


if __name__ == "__main__":
    unittest.main()
