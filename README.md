# English → U.S. Marine Translator

**Semper Translate.** A joke civilian-to-Marine speech degeneration engine — part dictionary, part RAH generator, zero official USMC doctrine.

![Semper Translate screenshot — add your image at docs/screenshot.png](https://raw.githubusercontent.com/WhiskeyCoder/Semper-Translate/refs/heads/main/images/English%20%E2%86%92%20U.S.%20Marine%20Translator.png)

> **Disclaimer:** This is a parody project. Terms like *moonshoes*, *assault purse*, and *knowledge sponge* are barracks humor — not real Marine Corps terminology. Do not cite this app at formation.

---

## What it does

Type normal English. Get back something between readable Marine slang and full motivational collapse:

| Civilian input | Marine output (example) |
|---|---|
| *"Please put your slippers on, dinner is ready."* | `RAH, devil, put your damn moonshoes on, chow is ready, killer.` |
| *"Where is the bathroom?"* | `Where is the head?` |
| *"I'm tired and want to go to bed."* | `this Marine smoked, RAH rack, YUT.` |
| *"Honey, pick up milk, bread, and eggs."* | `RAH, RAH RAH YUT RAAAH, OOORAH, RAH rAH RAH?` *(Sergeant Major mode)* |

**Translation confidence: 1775%**

---

## Features

- **Three dictionary modes**
  - **Authentic** — real USMC / naval terms (*head*, *deck*, *rack*, *chow*)
  - **Barracks** — common slang + humor (*moonshoes*, *go-juice*, *dick skinners*)
  - **Weapons-Grade Crayon** — full meme mode (*tactical Facebook machine*, *protein ordnance*)

- **Rah density slider** — Civilian (10%) → Boot (35%) → Staff NCO (65%) → Terminal Marine (90%) → Sergeant Major (100%)

- **Fun modes** — DI Mode, Motivational Poster, Radio Check

- **Toxic barracks toggle** — optional extra-edgy lexicon (off by default)

- **Word breakdown** — see what got substituted vs. what became RAH

- **CLI + GUI** — desktop app or terminal one-liners

---

## Quick start

### Requirements

- Python 3.10+
- **tkinter** (included with most Python installs on Windows/macOS; on Linux: `sudo apt install python3-tk`)

### Run the GUI

```bash
git clone https://github.com/YOUR_USERNAME/ENG-to-USMC.git
cd ENG-to-USMC
python main.py
```

### Run from the CLI

```bash
python -m eng_to_usmc "put your slippers on" -m barracks -d 35

python -m eng_to_usmc "move out now" -f di -d 65 --breakdown

python -m eng_to_usmc --list-modes
```

### CLI options

| Flag | Description |
|---|---|
| `-m`, `--mode` | `authentic`, `barracks`, `meme_corps` |
| `-d`, `--density` | Rah density 0–100 |
| `-p`, `--preset` | `Civilian`, `Boot`, `Staff NCO`, `Terminal Marine`, `Sergeant Major` |
| `-f`, `--fun` | `none`, `di`, `motivational`, `radio` |
| `--toxic` | Enable toxic barracks lexicon |
| `-s`, `--seed` | Fixed random seed (reproducible output) |
| `-b`, `--breakdown` | Print substitution log to stderr |

---

## Build a standalone `.exe` (Windows)

```bash
pip install pyinstaller
pyinstaller build.spec
```

Output: `dist/SemperTranslate.exe`

---

## Project structure

```
ENG-to-USMC/
├── main.py                 # Launch GUI
├── eng_to_usmc/
│   ├── engine.py           # Two-stage translator + RAH engine
│   ├── gui.py              # Tkinter UI
│   ├── cli.py              # Command-line interface
│   ├── context.py          # Head/bathroom disambiguation
│   └── fun_modes.py        # DI / motivational / radio post-processors
├── data/
│   ├── authentic.json      # Real USMC terms
│   ├── barracks.json       # Common slang
│   ├── meme_corps.json     # Meme / joke terms
│   ├── toxic.json          # Optional edgy terms
│   └── overrides.json      # Hand-tuned fixes
├── scripts/
│   └── import_lexicon.py   # Regenerate JSON from starter lexicon.md
├── tests/
│   └── test_engine.py
├── starter lexicon.md      # Source glossary (Marine → English reference)
└── docs/
    └── screenshot.png      # ← Add your screenshot here for the README
```

---

## Expanding the lexicon

1. Edit `starter lexicon.md` (reference tables) or the JSON files in `data/`
2. Regenerate from markdown:

```bash
python scripts/import_lexicon.py
```

3. Hand-tune edge cases in `data/overrides.json` (e.g. *head* = bathroom vs. skull)

---

## Run tests

```bash
python -m unittest discover -s tests -v
```

---

## Adding your screenshot

1. Take a screenshot of the app running (`python main.py`)
2. Save it as **`docs/screenshot.png`**
3. The image at the top of this README will display automatically

Optional: also add `docs/demo.gif` for an animated preview in the README.

---

## License

MIT — do whatever you want, but don't blame us if your gunny asks why you're calling slippers *moonshoes*.

---
Current Build: v1.775
*Moonshoes and knowledge sponges are not official USMC doctrine. This is satire and not affiliated with or supported by the USMC*
