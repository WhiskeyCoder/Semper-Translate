"""Context-aware disambiguation for ambiguous English terms."""

from __future__ import annotations

import re

# English "head" → bathroom (naval) vs skull/body
HEAD_BATHROOM_BEFORE = re.compile(
    r"\b(?:the|a|an|to|into|in|at|use|using|find|where(?:'s|\s+is|\s+are)?|"
    r"clean|visit|go\s+to)\s+$",
    re.IGNORECASE,
)
HEAD_BATHROOM_AFTER = re.compile(
    r"^\s*(?:is|are|was|were|room|door|stall|facility|break)\b",
    re.IGNORECASE,
)
HEAD_BODY_BEFORE = re.compile(
    r"\b(?:my|your|his|her|their|our|the|a|an|his|her|hit|hurt|bang|nod|shake|"
    r"turn|scratch|pat|hold|rest)\s+$",
    re.IGNORECASE,
)
HEAD_BODY_AFTER = re.compile(
    r"^\s*(?:hurts?|aches?|ache|pain|injury|cold|hot|bandage|wound|knock|"
    r"ache|spinning|pounding|splitting)\b",
    re.IGNORECASE,
)


def resolve_head(lower_text: str, start: int, end: int) -> str:
    """Return 'bathroom' or 'body' for English 'head' disambiguation."""
    before = lower_text[:start]
    after = lower_text[end:]

    if HEAD_BATHROOM_BEFORE.search(before) or HEAD_BATHROOM_AFTER.search(after):
        return "bathroom"
    if HEAD_BODY_BEFORE.search(before) or HEAD_BODY_AFTER.search(after):
        return "body"
    if re.search(r"\bwhere\b", before[-40:]):
        return "bathroom"
    return "body"
