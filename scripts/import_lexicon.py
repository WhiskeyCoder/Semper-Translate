#!/usr/bin/env python3
"""Import starter lexicon.md into data/*.json (English → Marine reverse mappings)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEXICON_MD = ROOT / "starter lexicon.md"
DATA_DIR = ROOT / "data"

MEME_MARINE_TERMS = {
    "moonshoes", "assault purse", "knowledge sponge", "tactical facebook machine",
    "foot prisons", "cancer stick", "eyeball ppe", "bcgs", "lifer blood",
    "protein ordnance", "tactical loaf", "white hydration", "boot-ass",
    "motivator", "dick skinners", "soup cooler", "booger hooks", "grape",
    "ink stick", "pogey bait", "goat rope", "clusterfuck", "soup sandwich",
    "boomstick", "pizza box", "gear queer", "cock holster", "moto boner",
    "charlie foxtrot", "shitshow", "barracks lawyer", "geardo",
}

TOXIC_MARINE_TERMS = {
    "dependapotamus", "dependa", "jody", "blue falcon", "buddy fucker",
    "barracks bunny",
}

SKIP_MARINE = {
    "marine", "map", "chow", "hump", "range", "qual", "motivated", "moto",
    "boot", "squared away", "tight", "salty", "tracking", "negative",
    "affirmative", "roger", "copy", "wilco", "semper fi", "oorah", "rah",
    "yut", "kill", "err", "g2g", "good to go", "outstanding", "carry on",
}

# English keys handled by context rules — skip auto-import
SKIP_ENGLISH = {"head", "skull", "skulls"}


def parse_tables(text: str) -> list[tuple[str, str, str]]:
    """Parse markdown table rows -> (marine_term, english, notes)."""
    rows: list[tuple[str, str, str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.count("|") < 3:
            continue
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) < 2:
            continue
        if cols[0].startswith("-") or cols[0].lower() in {"marine term", "marine slang", "term", "phrase"}:
            continue
        marine = cols[0].strip()
        english = cols[1].strip()
        notes = cols[2].strip() if len(cols) > 2 else ""
        if not marine or not english:
            continue
        rows.append((marine, english, notes))
    return rows


def split_english(english: str) -> list[str]:
    cleaned = re.sub(r"\*\*", "", english)
    cleaned = re.sub(r"\([^)]*\)", "", cleaned)
    parts = re.split(r"\s*/\s*|,\s*|\s+or\s+", cleaned, flags=re.IGNORECASE)
    result: list[str] = []
    for part in parts:
        part = part.strip().lower()
        part = re.sub(r"[^a-z0-9\s\-']", "", part).strip()
        if part and len(part) > 1 and part not in {"etc", "more", "army-heavy", "naval"}:
            result.append(part)
    return result


def classify(marine_lower: str, notes: str) -> set[str]:
    tiers: set[str] = {"authentic"}
    if any(t in marine_lower for t in MEME_MARINE_TERMS):
        tiers.add("meme_corps")
    if any(t in marine_lower for t in TOXIC_MARINE_TERMS):
        return {"toxic"}
    if "joking" in notes.lower() or "satirical" in notes.lower() or "teasing" in notes.lower():
        tiers.add("meme_corps")
    if "derogatory" in notes.lower() or "crude" in notes.lower() or "omit" in notes.lower():
        return {"toxic"}
    if marine_lower in MEME_MARINE_TERMS:
        tiers.add("meme_corps")
    else:
        tiers.add("barracks")
    return tiers


def merge_entry(target: dict, key: str, value: str) -> None:
    key = key.lower().strip()
    value = value.strip()
    if not key or not value or key == value.lower():
        return
    if key in SKIP_MARINE or key in SKIP_ENGLISH:
        return
    existing = target.get(key)
    if existing is None:
        target[key] = value
    elif isinstance(existing, list):
        if value not in existing:
            existing.append(value)
    elif existing != value:
        target[key] = [existing, value]


def load_json(name: str) -> dict:
    path = DATA_DIR / f"{name}.json"
    if path.exists():
        with path.open(encoding="utf-8") as f:
            return json.load(f)
    return {"phrases": {}, "words": {}}


def save_json(name: str, data: dict) -> None:
    path = DATA_DIR / f"{name}.json"
    # Single-word keys belong in words, not phrases
    for key in list(data["phrases"].keys()):
        if " " not in key:
            if key not in data["words"]:
                data["words"][key] = data["phrases"].pop(key)
            else:
                del data["phrases"][key]
    for bucket in ("phrases", "words"):
        data[bucket] = dict(sorted(data[bucket].items(), key=lambda x: x[0]))
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main() -> int:
    if not LEXICON_MD.exists():
        print(f"Missing {LEXICON_MD}", file=sys.stderr)
        return 1

    text = LEXICON_MD.read_text(encoding="utf-8")
    rows = parse_tables(text)

    tiers = {
        "authentic": load_json("authentic"),
        "barracks": load_json("barracks"),
        "meme_corps": load_json("meme_corps"),
        "toxic": load_json("toxic"),
    }

    imported = 0
    for marine, english, notes in rows:
        marine_lower = marine.lower()
        if marine_lower in SKIP_MARINE:
            continue
        english_parts = split_english(english)
        if not english_parts:
            continue

        row_tiers = classify(marine_lower, notes)
        if "toxic" in row_tiers:
            tier_list = ["toxic"]
        else:
            tier_list = sorted(row_tiers)

        for eng in english_parts:
            if eng in SKIP_ENGLISH:
                continue
            bucket = "phrases" if len(eng.split()) > 1 or len(marine.split()) > 1 else "words"

            for tier in tier_list:
                merge_entry(tiers[tier][bucket], eng, marine)
                imported += 1

    for name, data in tiers.items():
        save_json(name, data)
        print(f"Wrote {name}.json — {len(data['words'])} words, {len(data['phrases'])} phrases")

    print(f"Processed {len(rows)} table rows ({imported} mappings merged)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
