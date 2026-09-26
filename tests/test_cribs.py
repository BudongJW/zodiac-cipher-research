import unittest
from itertools import product

from zkc.cipher import load
from zkc.cribs import constrained_symbols, joint_placements, placements
from zkc.names import fits


class TestCribs(unittest.TestCase):
    z13 = load("z13").text
    z32 = load("z32").text

    def test_placements_respect_repeats(self):
        # ZODIAC 六个字母互不相同：窗口内不能含两个圈 8；第 8、13 位同为 M 也排除末尾位置
        self.assertEqual(placements(self.z13, "ZODIAC"), [0])
        self.assertEqual(placements("abab", "XYXY"), [0])
        self.assertEqual(placements("abab", "XYZW"), [])

    def test_z32_accepts_everything(self):
        self.assertEqual(len(placements(self.z32, "RADIANS")), 26)

    def test_joint_matches_brute_force(self):
        cipher = "abcadbe"
        cribs = ("AB", "CA")
        brute = []
        for p, q in product(range(6), repeat=2):
            if p + 2 > q and q + 2 > p:
                continue
            plain = ["?"] * 7
            ok = True
            for pos, crib in ((p, "AB"), (q, "CA")):
                for k, ch in enumerate(crib):
                    plain[pos + k] = ch
            mapping = {}
            for s, ch in zip(cipher, plain):
                if ch != "?" and mapping.setdefault(s, ch) != ch:
                    ok = False
            if ok:
                brute.append((p, q))
        self.assertEqual(sorted(joint_placements(cipher, cribs)), sorted(brute))

    def test_constrained_symbols(self):
        self.assertEqual(constrained_symbols(self.z32, "RADIANS", 0), 3)  # C、△、O 均在窗口外再次出现
        self.assertTrue(fits("ZODIACXYZWVZU", self.z13) is False)


if __name__ == "__main__":
    unittest.main()
