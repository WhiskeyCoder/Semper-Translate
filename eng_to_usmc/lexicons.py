"""Load and manage translation lexicons."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

MODES = {
    "authentic": "Authentic",
    "barracks": "Barracks",
    "meme_corps": "Weapons-Grade Crayon",
}


@dataclass
class Lexicon:
    phrases: dict[str, str | list[str]]
    words: dict[str, str | list[str]]
    _phrase_keys: list[str] = field(default=False, repr=False, compare=False)  # type: ignore[assignment]

    def __post_init__(self) -> None:
        object.__setattr__(self, "_phrase_keys", sorted(self.phrases.keys(), key=len, reverse=True))

    @classmethod
    def load(cls, mode: str, *, toxic: bool = False) -> Lexicon:
        path = DATA_DIR / f"{mode}.json"
        with path.open(encoding="utf-8") as f:
            data = json.load(f)

        phrases = cls._normalize_map(data.get("phrases", {}))
        words = cls._normalize_map(data.get("words", {}))

        overrides_path = DATA_DIR / "overrides.json"
        if overrides_path.exists():
            with overrides_path.open(encoding="utf-8") as f:
                overrides = json.load(f)
            phrases.update(cls._normalize_map(overrides.get("phrases", {})))
            words.update(cls._normalize_map(overrides.get("words", {})))

        if toxic:
            toxic_path = DATA_DIR / "toxic.json"
            if toxic_path.exists():
                with toxic_path.open(encoding="utf-8") as f:
                    toxic_data = json.load(f)
                phrases.update(cls._normalize_map(toxic_data.get("phrases", {})))
                words.update(cls._normalize_map(toxic_data.get("words", {})))

        return cls(phrases=phrases, words=words)

    @staticmethod
    def _normalize_map(raw: dict) -> dict[str, str | list[str]]:
        result: dict[str, str | list[str]] = {}
        for key, value in raw.items():
            result[key.lower()] = value
        return result

    def phrase_keys_by_length(self) -> list[str]:
        return self._phrase_keys

    def pick(self, key: str, rng) -> str | None:
        if " " in key:
            entry = self.phrases.get(key) or self.words.get(key)
        else:
            entry = self.words.get(key) or self.phrases.get(key)
        if entry is None:
            return None
        if isinstance(entry, list):
            return rng.choice(entry)
        return entry


def load_lexicon(mode: str, *, toxic: bool = False) -> Lexicon:
    if mode not in MODES:
        raise ValueError(f"Unknown mode: {mode}. Choose from {list(MODES)}")
    return Lexicon.load(mode, toxic=toxic)
