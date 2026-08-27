"""Core English → U.S. Marine translation engine."""

from __future__ import annotations

import random
import re
import time
from dataclasses import dataclass, field

from eng_to_usmc.context import resolve_head
from eng_to_usmc.fun_modes import apply_fun_mode
from eng_to_usmc.lexicons import Lexicon, load_lexicon

# Random RAH pool when no fixed mapping exists
RAH_FORMS: list[tuple[str, float]] = [
    ("RAH", 30),
    ("rah", 10),
    ("rAH", 8),
    ("RAHRAH", 12),
    ("RAAAH", 8),
    ("RAAAAHHH", 4),
    ("YUT", 7),
    ("ERR", 5),
    ("KILL", 5),
    ("OOORAH", 10),
    ("OOH-RAH", 3),
    ("Rrraaah", 3),
    ("RAH-RAH", 2),
    ("RAH RAH", 2),
    ("RAHRAHRAH", 2),
]

# Per-word fixed outputs when RAH degeneration fires (idea.txt)
FIXED_RAH_TRIGGERS: dict[str, str] = {
    "the": "RAH",
    "a": "rah",
    "an": "rah",
    "and": "RAHRAH",
    "but": "rAH",
    "so": "RAAAH",
    "can": "RAH",
    "could": "rAH",
    "would": "RAH-RAH",
    "is": "rah",
    "are": "RAH",
    "please": "RAH, devil,",
    "because": "RAH BECAUSE RAH",
}

# Always-substitute pronouns (stage 1 semantic mapping)
PRONOUN_MAP: dict[str, str] = {
    "you": "devil",
    "your": "your damn",
    "my": "this Marine's",
    "i": "this Marine",
    "me": "this Marine",
    "we": "this platoon",
    "our": "our damn",
    "they": "those motivators",
    "them": "those devils",
    "their": "their damn",
    "he": "that devil",
    "she": "that killer",
    "him": "that devil",
    "her": "that killer",
    "his": "that devil's",
}

# Generic filler words that may become random RAH
GENERIC_RAH_WORDS = frozenset(
    {
        "was", "were", "be", "to", "of", "in", "on", "at", "for", "with", "from",
        "that", "this", "it", "do", "did", "have", "has", "had", "will", "shall",
        "should", "may", "might", "must", "if", "when", "where", "what", "who",
        "why", "how", "not", "or", "nor", "by", "up", "down", "out", "about",
        "into", "over", "after", "before", "between", "through", "during",
        "without", "within", "along", "across", "against", "among", "around",
        "behind", "below", "beneath", "beside", "beyond", "despite", "except",
        "inside", "near", "off", "onto", "outside", "since", "toward", "towards",
        "under", "until", "upon", "while",
    }
)

DENSITY_PRESETS: dict[str, int] = {
    "Civilian": 10,
    "Boot": 35,
    "Staff NCO": 65,
    "Terminal Marine": 90,
    "Sergeant Major": 100,
}

TOKEN_PATTERN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?|[^\w\s]|\s+")
WORD_PATTERN = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")


@dataclass
class WordChange:
    original: str
    replacement: str
    change_type: str  # lexicon, pronoun, rah, context, unchanged


@dataclass
class TranslationStats:
    confidence: int
    readiness: str
    motivation: str
    crayon_level: str


@dataclass
class TranslationResult:
    text: str
    confidence: int
    stats: TranslationStats
    breakdown: list[WordChange] = field(default_factory=list)
    mode: str = "barracks"
    density: int = 35
    fun_mode: str = "none"
    seed: int = 0
    rah_count: int = 0
    lexicon_count: int = 0


class MarineTranslator:
    def __init__(
        self,
        mode: str = "barracks",
        density: int = 35,
        *,
        fun_mode: str = "none",
        toxic: bool = False,
        seed: int | None = None,
    ):
        self.mode = mode
        self.density = max(0, min(100, density))
        self.fun_mode = fun_mode
        self.toxic = toxic
        self.lexicon = load_lexicon(mode, toxic=toxic)
        self._seed = seed if seed is not None else int(time.time() * 1000) % 1_000_000
        self._rng = random.Random(self._seed)
        self._breakdown: list[WordChange] = []
        self._rah_count = 0
        self._lexicon_count = 0

    def translate(self, text: str) -> TranslationResult:
        self._breakdown = []
        self._rah_count = 0
        self._lexicon_count = 0

        stripped = text.strip()
        if not stripped:
            return self._result("ERROR 1775: CIVILIAN LANGUAGE DETECTED.", empty=True)

        if self.density >= 100:
            output = self._sergeant_major_mode(stripped)
            output = apply_fun_mode(output, self.fun_mode, self._rng)
            return self._result(output)

        # Stage 1: lexicon + pronouns + context (clean pass)
        stage1 = self._substitute_lexicon(stripped)

        # Stage 2: RAH degeneration on remaining tokens
        output = self._apply_rah(stage1, stripped.lower())

        # Stage 3: polish
        output = self._add_devil_suffix(output)
        output = self._maybe_add_trackin(output)
        output = apply_fun_mode(output, self.fun_mode, self._rng)

        return self._result(output)

    def _result(self, text: str, *, empty: bool = False) -> TranslationResult:
        stats = self._build_stats(empty)
        return TranslationResult(
            text=text,
            confidence=stats.confidence,
            stats=stats,
            breakdown=list(self._breakdown),
            mode=self.mode,
            density=self.density,
            fun_mode=self.fun_mode,
            seed=self._seed,
            rah_count=self._rah_count,
            lexicon_count=self._lexicon_count,
        )

    def _build_stats(self, empty: bool) -> TranslationStats:
        if empty:
            return TranslationStats(1775, "UNSAT", "CRITICAL", "ELEVATED")

        base = 1775 + self._rng.randint(-12, 48)
        readiness = self._rng.choice(["SAT", "UNSAT", "G2G", "NO-GO", "TRACKING"])
        if self.density >= 90:
            readiness = "UNSAT"
        elif self.density <= 15:
            readiness = "G2G"

        motivation = self._rng.choice(["HIGH", "CRITICAL", "MOTO BONER", "LOW-SPEED", "TERMINAL"])
        crayon = self._rng.choice(["MINIMAL", "ELEVATED", "WEAPONS-GRADE", "CRITICAL MASS"])

        return TranslationStats(base, readiness, motivation, crayon)

    def _sergeant_major_mode(self, text: str) -> str:
        # ~35% chance entire sentence collapses to one RAH
        if self._rng.random() < 0.35:
            punct = "?" if "?" in text else "."
            return f"RAH{punct}"

        parts: list[str] = []
        for match in TOKEN_PATTERN.finditer(text):
            token = match.group()
            if token.isspace() or re.fullmatch(r"[^\w\s]", token):
                parts.append(token)
            else:
                parts.append(self._pick_rah())
                self._rah_count += 1
                self._breakdown.append(WordChange(token, parts[-1], "rah"))
        return "".join(parts).strip()

    def _substitute_lexicon(self, text: str) -> str:
        lower = text.lower()
        phrase_map = self._build_phrase_spans(lower)
        parts: list[str] = []
        i = 0

        while i < len(text):
            if text[i].isspace():
                parts.append(text[i])
                i += 1
                continue

            if phrase_map.get(i):
                replacement, length, original = phrase_map[i]
                # Context override for ambiguous English "head" caught as phrase
                if original.lower() == "head":
                    kind = resolve_head(lower, i, i + length)
                    replacement = "head" if kind == "bathroom" else (
                        self.lexicon.pick("head", self._rng) or "grape"
                    )
                    self._breakdown.append(WordChange(original, replacement, "context"))
                else:
                    self._breakdown.append(WordChange(original, replacement, "lexicon"))
                parts.append(replacement)
                self._lexicon_count += 1
                i += length
                continue

            punct_match = re.match(r"[^\w\s]", text[i:])
            if punct_match:
                parts.append(punct_match.group())
                i += len(punct_match.group())
                continue

            word_match = re.match(r"[A-Za-z]+(?:'[A-Za-z]+)?", text[i:])
            if not word_match:
                parts.append(text[i])
                i += 1
                continue

            word = word_match.group()
            lower_word = word.lower()
            i += len(word)

            if lower_word == "head":
                kind = resolve_head(lower, i - len(word), i)
                if kind == "bathroom":
                    picked = "head"
                else:
                    picked = self.lexicon.pick("head", self._rng) or "grape"
                parts.append(picked)
                self._lexicon_count += 1
                self._breakdown.append(WordChange(word, picked, "context"))
                continue

            picked = self.lexicon.pick(lower_word, self._rng)
            if picked is not None:
                parts.append(picked)
                self._lexicon_count += 1
                self._breakdown.append(WordChange(word, picked, "lexicon"))
                continue

            if lower_word in PRONOUN_MAP and self.density >= 5:
                replacement = PRONOUN_MAP[lower_word]
                parts.append(replacement)
                self._breakdown.append(WordChange(word, replacement, "pronoun"))
                continue

            parts.append(word)
            self._breakdown.append(WordChange(word, word, "unchanged"))

        return "".join(parts)

    def _protected_terms(self) -> frozenset[str]:
        terms: set[str] = set()
        for change in self._breakdown:
            if change.change_type in ("lexicon", "context", "pronoun"):
                for word in WORD_PATTERN.findall(change.replacement):
                    terms.add(word.lower())
        return frozenset(terms)

    def _apply_rah(self, text: str, original_lower: str) -> str:
        if self.density <= 0:
            return text

        protected = self._protected_terms()
        segments: list[tuple[str, str | None]] = []
        last = 0
        word_matches = list(WORD_PATTERN.finditer(text))
        total_words = len(word_matches)

        for match in word_matches:
            segments.append(("text", text[last : match.start()]))
            segments.append(("word", match.group()))
            last = match.end()
        segments.append(("text", text[last:]))

        word_index = 0
        output: list[str] = []

        for kind, value in segments:
            if kind == "text":
                output.append(value)
                continue

            word = value
            lower_word = word.lower()

            if lower_word in protected:
                output.append(word)
                continue

            position_boost = int((word_index / max(total_words - 1, 1)) * 15)
            effective_density = min(100, self.density + position_boost)
            word_index += 1

            replacement: str | None = None

            if lower_word in FIXED_RAH_TRIGGERS:
                if self._rng.randint(1, 100) <= effective_density:
                    replacement = FIXED_RAH_TRIGGERS[lower_word]
            elif lower_word in GENERIC_RAH_WORDS:
                if self._rng.randint(1, 100) <= effective_density:
                    replacement = self._pick_rah()
            elif self._is_unchanged_lexicon_word(lower_word):
                if self._rng.randint(1, 100) <= max(0, effective_density - 25):
                    if self._rng.randint(1, 100) <= 95:
                        replacement = self._pick_rah()
            elif self._rng.randint(1, 100) <= max(0, effective_density - 50):
                replacement = self._pick_rah()

            if replacement is not None:
                output.append(replacement)
                self._rah_count += 1
                self._breakdown.append(WordChange(word, replacement, "rah"))
            else:
                output.append(word)

        return "".join(output)

    def _is_unchanged_lexicon_word(self, lower_word: str) -> bool:
        for change in self._breakdown:
            if change.original.lower() == lower_word and change.change_type == "unchanged":
                return True
        return False

    def _build_phrase_spans(self, lower_text: str) -> dict[int, tuple[str, int, str]]:
        spans: dict[int, tuple[str, int, str]] = {}
        for phrase in self.lexicon.phrase_keys_by_length():
            pattern = re.compile(r"\b" + re.escape(phrase) + r"\b")
            for match in pattern.finditer(lower_text):
                start = match.start()
                if any(start <= pos < start + len(phrase) for pos in spans):
                    continue
                picked = self.lexicon.pick(phrase, self._rng)
                if picked:
                    spans[start] = (picked, len(phrase), match.group())
        return spans

    def _pick_rah(self) -> str:
        total = sum(weight for _, weight in RAH_FORMS)
        roll = self._rng.uniform(0, total)
        cumulative = 0.0
        for form, weight in RAH_FORMS:
            cumulative += weight
            if roll <= cumulative:
                return form
        return "RAH"

    def _add_devil_suffix(self, text: str) -> str:
        if self.density < 15:
            return text
        if text.rstrip().endswith((".", "!", "?")):
            base = text.rstrip()
            punct = base[-1]
            body = base[:-1].rstrip()
            if self._rng.randint(1, 100) <= min(self.density, 75):
                suffix = self._rng.choice([", devil.", ", killer.", ", motivator.", "."])
                if suffix != ".":
                    return f"{body}{suffix}"
                return f"{body}{punct}"
        elif self.density >= 45 and self._rng.randint(1, 100) <= 25:
            return f"{text.rstrip()}, devil."
        return text

    def _maybe_add_trackin(self, text: str) -> str:
        if "?" in text and self.density >= 25 and self._rng.randint(1, 100) <= 40:
            return f"{text.rstrip()} TRACKIN'?"
        return text


def translate(
    text: str,
    mode: str = "barracks",
    density: int = 35,
    *,
    fun_mode: str = "none",
    toxic: bool = False,
    seed: int | None = None,
) -> TranslationResult:
    return MarineTranslator(
        mode=mode,
        density=density,
        fun_mode=fun_mode,
        toxic=toxic,
        seed=seed,
    ).translate(text)


def format_breakdown(result: TranslationResult) -> str:
    lines: list[str] = []
    for change in result.breakdown:
        if change.change_type == "unchanged":
            continue
        arrow = f"{change.original} → {change.replacement}"
        tag = change.change_type.upper()
        lines.append(f"  [{tag}] {arrow}")

    if not lines:
        return "  (no substitutions — increase density or add lexicon hits)"

    summary = f"{result.lexicon_count} lexicon · {result.rah_count} RAH"
    return summary + "\n" + "\n".join(lines[:40]) + (
        f"\n  ... +{len(lines) - 40} more" if len(lines) > 40 else ""
    )
