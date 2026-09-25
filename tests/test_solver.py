import os
import random
import unittest

from zkc.corpus import builtin_model
from zkc.ngram import ALPHABET, NgramModel, encode
from zkc.solver import solve

# 与 Zodiac 无关的测试明文
SAMPLE = (
    "The history of secret writing is long and full of surprises. Every era produced "
    "people who believed their messages could never be read, and every era produced "
    "others who proved them wrong. A good cipher hides the patterns of the language, "
    "but a careless writer leaves traces behind: repeated words, favourite phrases and "
    "small mistakes that a patient analyst can follow one step at a time until the whole "
    "message is clear."
)
SYMBOLS = "0123456789abcdefghijklmnopqrstuvwxyz!#$%&*+-=?@^_~<>"


def encrypt(plain: str, homophones: int, seed: int) -> tuple[str, dict[str, str]]:
    """随机密钥加密：每个字母分配 homophones 个符号，按顺序轮换使用。"""
    rng = random.Random(seed)
    pool = list(SYMBOLS)
    rng.shuffle(pool)
    table = {ch: [pool.pop() for _ in range(homophones)] for ch in ALPHABET}
    turn = dict.fromkeys(ALPHABET, 0)
    out = []
    for ch in plain:
        out.append(table[ch][turn[ch] % homophones])
        turn[ch] += 1
    key = {s: ch for ch, syms in table.items() for s in syms}
    return "".join(out), key


class TestSolver(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = builtin_model(4)
        cls.plain = "".join(ALPHABET[i] for i in encode(SAMPLE))

    def test_simple_substitution(self):
        cipher, _ = encrypt(self.plain, 1, seed=7)
        best = solve(cipher, self.model, restarts=2, sweeps=300, seed=3)[0]
        hits = sum(a == b for a, b in zip(best.plaintext, self.plain))
        self.assertGreater(hits / len(self.plain), 0.95)

    def test_fixed_symbols_are_kept(self):
        cipher, key = encrypt(self.plain, 1, seed=7)
        sym = cipher[0]
        best = solve(cipher, self.model, restarts=1, sweeps=20, seed=0, fixed={sym: "Q"})[0]
        self.assertEqual(best.key[sym], "Q")

    def test_from_corpus_model(self):
        m = NgramModel.from_corpus(self.plain * 3, 3)
        self.assertEqual(m.table.shape, (26 ** 3,))
        self.assertGreater(m.score(self.plain), m.score(self.plain[::-1]))


@unittest.skipUnless(os.environ.get("ZKC_SLOW"), "set ZKC_SLOW=1 to run slow blind-solve tests")
class TestBlindReproduction(unittest.TestCase):
    def test_z408_blind(self):
        from zkc.reproduce import blind_solve
        results, acc = blind_solve("z408", builtin_model(4), restarts=8, sweeps=2000,
                                   seed=1, jobs=os.cpu_count() or 1)
        self.assertGreater(acc[0], 0.75)


if __name__ == "__main__":
    unittest.main()
