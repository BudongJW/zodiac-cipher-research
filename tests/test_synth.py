import random
import unittest

from zkc.keys import derive_key
from zkc.synth import encrypt, homophone_counts, random_key, sample_window, zodiac_plaintexts


class TestSynth(unittest.TestCase):
    def test_corpus(self):
        texts = zodiac_plaintexts()
        self.assertEqual([len(t) for t in texts], [390, 340])
        self.assertTrue(texts[0].startswith("ILIKEKILLINGPEOPLE"))

    def test_homophone_counts(self):
        counts = homophone_counts("z340")
        self.assertEqual(counts["E"], 6)
        self.assertEqual(counts["T"], 6)
        self.assertTrue(all(v >= 1 for v in counts.values()))

    def test_cycle_encryption_is_consistent(self):
        rng = random.Random(1)
        plain = sample_window(zodiac_plaintexts(), 60, rng)
        key = random_key(homophone_counts("z340"), rng)
        cipher = encrypt(plain, key, "cycle", rng)
        derived = derive_key(cipher, plain)  # 每个符号只对应一个字母
        for sym, letter in derived.items():
            self.assertIn(sym, key[letter])
        # 轮换：连续出现的同一字母依次使用不同的同音符号
        e_syms = [c for c, p in zip(cipher, plain) if p == "E"]
        self.assertGreater(len(key["E"]), 1)
        for a, b in zip(e_syms, e_syms[1:]):
            self.assertNotEqual(a, b)


if __name__ == "__main__":
    unittest.main()
