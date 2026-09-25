import unittest

from zkc.keys import KeyConflict, apply_key, derive_key, plaintext_accuracy, symbol_accuracy
from zkc.reproduce import reference_key, verify_z408


class TestKeys(unittest.TestCase):
    def test_derive_and_apply(self):
        key = derive_key("abca", "THET")
        self.assertEqual(key, {"a": "T", "b": "H", "c": "E"})
        self.assertEqual(apply_key("cab?", key), "ETH?")

    def test_conflict(self):
        with self.assertRaises(KeyConflict):
            derive_key("aa", "TE")

    def test_accuracy(self):
        ref = {"a": "T", "b": "H", "c": "E"}
        guess = {"a": "T", "b": "H", "c": "A"}
        self.assertAlmostEqual(plaintext_accuracy("aabc", guess, ref), 0.75)
        self.assertAlmostEqual(symbol_accuracy(guess, ref), 2 / 3)

    def test_reference_keys(self):
        self.assertEqual(len(reference_key("z408")), 54)
        self.assertEqual(len(reference_key("z340")), 63)
        self.assertTrue(verify_z408().plaintext_matches)


if __name__ == "__main__":
    unittest.main()
