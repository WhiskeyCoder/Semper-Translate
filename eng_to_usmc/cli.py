"""CLI for English → U.S. Marine translator."""

from __future__ import annotations

import argparse
import sys

from eng_to_usmc.engine import DENSITY_PRESETS, format_breakdown, translate
from eng_to_usmc.fun_modes import FUN_MODES
from eng_to_usmc.lexicons import MODES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="English → U.S. Marine joke translator",
        prog="python -m eng_to_usmc",
    )
    parser.add_argument("text", nargs="?", help="Text to translate")
    parser.add_argument(
        "--mode", "-m",
        choices=list(MODES.keys()),
        default="barracks",
        help="Dictionary mode",
    )
    parser.add_argument(
        "--density", "-d",
        type=int,
        default=35,
        help="Rah density 0–100",
    )
    parser.add_argument(
        "--preset", "-p",
        choices=list(DENSITY_PRESETS.keys()),
        help="Density preset (overrides --density)",
    )
    parser.add_argument(
        "--fun", "-f",
        choices=list(FUN_MODES.keys()),
        default="none",
        help="Fun post-processing mode",
    )
    parser.add_argument("--toxic", action="store_true", help="Enable toxic barracks lexicon")
    parser.add_argument("--seed", "-s", type=int, help="Random seed for reproducible output")
    parser.add_argument("--breakdown", "-b", action="store_true", help="Show word breakdown")
    parser.add_argument("--list-modes", action="store_true", help="List dictionary modes")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_modes:
        for key, label in MODES.items():
            print(f"  {key}: {label}")
        return 0

    text = args.text
    if not text:
        text = sys.stdin.read()

    density = DENSITY_PRESETS[args.preset] if args.preset else args.density

    result = translate(
        text,
        mode=args.mode,
        density=density,
        fun_mode=args.fun,
        toxic=args.toxic,
        seed=args.seed,
    )

    print(result.text)
    print(
        f"\n[{MODES[result.mode]} · {result.density}% · confidence {result.confidence}% · "
        f"readiness {result.stats.readiness} · motivation {result.stats.motivation}]",
        file=sys.stderr,
    )

    if args.breakdown:
        print(format_breakdown(result), file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
