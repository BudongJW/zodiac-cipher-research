import unittest

from zkc.cipher import load
from zkc.evaluate import consistency, key_agreement, pattern_base_rate
from zkc.reproduce import reference_key


class TestEvaluate(unittest.TestCase):
    z13 = load("z13").text
    z32 = load("z32").text

    def test_consistency(self):
        garlick = consistency(self.z13, "DREATATOTPEDO")
        self.assertTrue(garlick["fits_homophonic"])
        self.assertEqual(garlick["min_errors"], 0)
        bauer = consistency(self.z13, "ALFREDENEUMAN")
        self.assertFalse(bauer["fits_homophonic"])
        self.assertEqual(bauer["min_errors"], 1)      # 两个 N → F / M
        stewart = consistency(self.z13, "EARLVANBESTJR")
        self.assertEqual(stewart["min_errors"], 5)
        grinell = consistency(self.z32, "ESTIMATEFOURRADIANSANDFIVEINCHES")
        self.assertTrue(grinell["fits_homophonic"])

    def test_key_agreement(self):
        # Garlick 的读法直接取自 Z340 密钥，共有符号上应完全一致
        ka = key_agreement(self.z13, "DREATATOTPEDO", reference_key("z340"))
        self.assertEqual(ka["shared_positions"], 9)
        self.assertEqual(ka["matches"], 9)
        self.assertLess(ka["p_value"], 1e-6)
        # 与 Z408 密钥则无特别一致
        ka408 = key_agreement(self.z13, "DREATATOTPEDO", reference_key("z408"))
        self.assertGreater(ka408["p_value"], 0.01)

    def test_pattern_base_rate(self):
        r = pattern_base_rate("ab", ["XYZXYZ"], min_distinct=1)
        self.assertEqual(r, {"windows": 5, "fits": 5, "rate": 1.0})
        r = pattern_base_rate("aa", ["XXYZ"], min_distinct=1)
        self.assertEqual(r["fits"], 1)


if __name__ == "__main__":
    unittest.main()
