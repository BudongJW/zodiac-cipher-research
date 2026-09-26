import unittest

from zkc.cipher import load
from zkc.evaluate import consistency, grade, key_agreement, pattern_base_rate, score_claim
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

    def test_grade(self):
        self.assertEqual(grade(None, False, None), "D")
        self.assertEqual(grade(False, False, 1e-9), "C")
        self.assertEqual(grade(True, True, 1e-9), "C")
        self.assertEqual(grade(True, False, 0.2), "B")
        self.assertEqual(grade(True, False, 1e-5), "A")

    def test_score_claim(self):
        refs = {"z340": reference_key("z340"), "z408": reference_key("z408")}
        garlick = score_claim(self.z13, "DREATATOTPEDO", references=refs, key_source="z340")
        self.assertEqual(garlick["grade"], "B")  # Z340 一致是构造所致，不计为独立证据
        # 若不声明 key_source，则 9/9 的一致会被当作独立证据
        self.assertEqual(score_claim(self.z13, "DREATATOTPEDO", references=refs)["grade"], "A")
        self.assertEqual(score_claim(self.z13, "MARVINMERRILL", references=refs)["grade"], "C")

    def test_pattern_base_rate(self):
        r = pattern_base_rate("ab", ["XYZXYZ"], min_distinct=1)
        self.assertEqual(r, {"windows": 5, "fits": 5, "rate": 1.0})
        r = pattern_base_rate("aa", ["XXYZ"], min_distinct=1)
        self.assertEqual(r["fits"], 1)


if __name__ == "__main__":
    unittest.main()
