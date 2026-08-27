"""Tests for the English → U.S. Marine translator."""

from __future__ import annotations

import unittest

from eng_to_usmc.engine import MarineTranslator, translate
from eng_to_usmc.fun_modes import apply_fun_mode


class TestMarineTranslator(unittest.TestCase):
    def test_empty_input_error(self) -> None:
        result = translate("   ", seed=1)
        self.assertIn("ERROR 1775", result.text)

    def test_low_density_readable(self) -> None:
        result = translate(
            "put your slippers on",
            mode="barracks",
            density=10,
            seed=42,
        )
        self.assertIn("moonshoes", result.text.lower())
        self.assertLess(result.rah_count, 3)

    def test_lexicon_substitution(self) -> None:
        result = translate(
            "the bathroom is upstairs",
            mode="authentic",
            density=0,
            seed=1,
        )
        self.assertIn("head", result.text.lower())

    def test_head_disambiguation_body(self) -> None:
        t = MarineTranslator(mode="barracks", density=0, seed=1)
        result = t.translate("my head hurts")
        self.assertIn("grape", result.text.lower())

    def test_head_disambiguation_bathroom(self) -> None:
        t = MarineTranslator(mode="authentic", density=0, seed=1)
        result = t.translate("where is the head")
        lowered = result.text.lower()
        self.assertIn("head", lowered)
        self.assertNotIn("grape", lowered)

    def test_sergeant_major_can_collapse(self) -> None:
        results = {
            translate("hello world test", density=100, seed=s).text
            for s in range(20)
        }
        self.assertTrue(any(r in {"RAH.", "RAH"} or r.startswith("RAH") for r in results))

    def test_high_density_has_rah(self) -> None:
        result = translate(
            "Can you put your slippers beside the door before dinner?",
            mode="meme_corps",
            density=90,
            seed=7,
        )
        self.assertGreater(result.rah_count, 0)
        self.assertIn("moonshoes", result.text.lower())

    def test_breakdown_tracks_changes(self) -> None:
        result = translate("slippers and shoes", mode="barracks", density=0, seed=1)
        self.assertGreater(result.lexicon_count, 0)
        types = {c.change_type for c in result.breakdown}
        self.assertIn("lexicon", types)

    def test_fun_di_mode(self) -> None:
        import random

        rng = random.Random(1)
        out = apply_fun_mode("move out now?", "di", rng)
        self.assertTrue(out.startswith("LOCK IT UP"))
        self.assertEqual(out, out.upper())

    def test_fun_motivational_mode(self) -> None:
        import random

        rng = random.Random(1)
        out = apply_fun_mode("get chow", "motivational", rng)
        self.assertIn("get chow", out)
        self.assertIn('"', out)

    def test_toxic_mode(self) -> None:
        result = translate("my partner left", mode="meme_corps", density=0, toxic=True, seed=1)
        lowered = result.text.lower()
        self.assertTrue("jody" in lowered or "dependa" in lowered or "devil" in lowered)

    def test_seed_reproducibility(self) -> None:
        a = translate("hello devil friend", seed=99)
        b = translate("hello devil friend", seed=99)
        self.assertEqual(a.text, b.text)


if __name__ == "__main__":
    unittest.main()
