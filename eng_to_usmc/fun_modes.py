"""Optional post-processing style modes."""

from __future__ import annotations

import random
import re

FUN_MODES = {
    "none": "Standard",
    "di": "DI Mode",
    "motivational": "Motivational Poster",
    "radio": "Radio Check",
}

MOTIVATIONAL_WRAPPERS = [
    '"Pain is weakness leaving the body." — {text}',
    '"Improvise, adapt, overcome." — {text}',
    '"Embrace the suck." — {text}',
    '"Every Marine a rifleman." — {text}',
    '"Welcome to the Marine Corps." — {text}',
]

RADIO_PREFIXES = ["COPY.", "ROGER.", "WILCO.", "LOUD AND CLEAR."]
RADIO_SUFFIXES = ["OVER.", "OUT.", "SAY AGAIN, OVER."]


def apply_fun_mode(text: str, mode: str, rng: random.Random) -> str:
    if not text or mode == "none":
        return text

    if mode == "di":
        return _di_mode(text)

    if mode == "motivational":
        wrapper = rng.choice(MOTIVATIONAL_WRAPPERS)
        return wrapper.format(text=text)

    if mode == "radio":
        prefix = rng.choice(RADIO_PREFIXES)
        suffix = rng.choice(RADIO_SUFFIXES)
        return f"{prefix} {text} {suffix}"

    return text


def _di_mode(text: str) -> str:
    upper = text.upper()
    if not upper.startswith("LOCK IT UP"):
        upper = f"LOCK IT UP. {upper}"
    if "?" in text and "SAY AGAIN" not in upper:
        upper = upper.rstrip(".!") + ". SAY AGAIN?"
    return upper
