import unittest

from zkc.reproduce import verify_z340
from zkc.transpose import decimation, is_permutation, transpose, untranspose, z340_order


class TestTranspose(unittest.TestCase):
    def test_decimation_covers_grid(self):
        cells = decimation(9, 17, 1, 2)
        self.assertEqual(len(set(cells)), 153)
        self.assertEqual(cells[:4], [(0, 0), (1, 2), (2, 4), (3, 6)])

    def test_decimation_rejects_non_covering_step(self):
        with self.assertRaises(ValueError):
            decimation(9, 17, 3, 0)

    def test_roundtrip(self):
        order = z340_order()
        text = "".join(chr(0x4E00 + i) for i in range(340))
        self.assertEqual(transpose(untranspose(text, order), order), text)

    def test_z340_order(self):
        order = z340_order()
        self.assertTrue(is_permutation(order, 340))
        self.assertEqual(order[:3], [0, 19, 38])  # (0,0) → (1,2) → (2,4)

    def test_z340_published_scheme_reproduces_plaintext(self):
        self.assertTrue(verify_z340().plaintext_matches)


if __name__ == "__main__":
    unittest.main()
