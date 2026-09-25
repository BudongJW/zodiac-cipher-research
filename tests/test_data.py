import unittest

from zkc.cipher import load
from zkc.stats import overlap_table


class TestTranscriptions(unittest.TestCase):
    def test_dimensions(self):
        expected = {  # 名称: (行数, 长度, 不同符号)
            "z408": (24, 408, 54),
            "z340": (20, 340, 63),
            "z13": (1, 13, 8),
            "z32": (2, 32, 29),
        }
        for name, (rows, length, distinct) in expected.items():
            c = load(name)
            with self.subTest(name=name):
                self.assertEqual(c.height, rows)
                self.assertEqual(len(c), length)
                self.assertEqual(len(c.symbols), distinct)

    def test_grids(self):
        self.assertTrue(load("z408").is_grid)
        self.assertTrue(load("z340").is_grid)
        self.assertEqual([len(r) for r in load("z32").rows], [17, 15])

    def test_unsolved_transcriptions(self):
        # 与 Oranchak Wiki 原始 wikitext 核对一致（2026-09-25）
        self.assertEqual(load("z13").text, "AENz0K0M0[NAM")
        self.assertEqual(load("z32").rows, ("C9J|#Ok[AMf8?ORTG", "X6FDVj%HCELzPW9"))

    def test_symbol_overlap(self):
        texts = {n: load(n).text for n in ("z408", "z340", "z13", "z32")}
        t = overlap_table(texts)
        self.assertEqual(t[("z408", "z340")], 47)
        self.assertEqual(t[("z32", "z408")], 25)
        self.assertEqual(t[("z32", "z340")], 27)
        self.assertEqual(t[("z13", "z408")], 6)
        self.assertEqual(t[("z13", "z340")], 6)
        self.assertEqual(t[("z13", "z32")], 5)
        solved = set(texts["z408"]) | set(texts["z340"])
        self.assertEqual(set(texts["z13"]) - solved, {"0", "["})
        self.assertEqual(set(texts["z32"]) - solved, {"?", "["})


if __name__ == "__main__":
    unittest.main()
