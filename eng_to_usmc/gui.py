"""Tkinter GUI for the English → U.S. Marine translator."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from eng_to_usmc.engine import DENSITY_PRESETS, format_breakdown, translate
from eng_to_usmc.fun_modes import FUN_MODES
from eng_to_usmc.lexicons import MODES

COLORS = {
    "bg": "#1a1f16",
    "panel": "#252b20",
    "gold": "#c4a035",
    "gold_dim": "#8a7328",
    "text": "#e8e4d9",
    "text_dim": "#9a9688",
    "accent": "#8b0000",
    "input_bg": "#0f120d",
    "button": "#3d4a2f",
    "button_hover": "#4d5c3b",
}

EXAMPLE_SENTENCES = [
    "Please put your slippers on and come downstairs, dinner is ready.",
    "Where did you put my coffee?",
    "Excuse me, could you tell me where the bathroom is?",
    "I'm tired and I want to go to bed.",
    "Honey, can you pick up milk, bread, and eggs on your way home?",
    "You get your slippers in line.",
    "My head hurts but I need to use the head before chow.",
]

LIVE_DEBOUNCE_MS = 450


class MarineTranslatorApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("English → U.S. Marine Translator")
        self.geometry("920x820")
        self.minsize(720, 680)
        self.configure(bg=COLORS["bg"])

        self._mode_key_var = tk.StringVar(value="barracks")
        self._mode_display_var = tk.StringVar(value=MODES["barracks"])
        self._density_var = tk.IntVar(value=35)
        self._density_label_var = tk.StringVar(value="Boot (35%)")
        self._fun_display_var = tk.StringVar(value=FUN_MODES["none"])
        self._fun_key_var = tk.StringVar(value="none")
        self._toxic_var = tk.BooleanVar(value=False)
        self._live_var = tk.BooleanVar(value=True)
        self._confidence_var = tk.StringVar(value="Translation confidence: —")
        self._stats_var = tk.StringVar(value="")
        self._last_seed: int | None = None
        self._live_job: str | None = None

        self._build_ui()
        self._bind_events()
        self.after(200, self._do_translate)

    def _build_ui(self) -> None:
        self._configure_styles()
        container = tk.Frame(self, bg=COLORS["bg"], padx=20, pady=16)
        container.pack(fill=tk.BOTH, expand=True)

        self._build_header(container)
        self._build_controls(container)
        self._build_examples(container)
        self._build_io_panels(container)
        self._build_breakdown(container)
        self._build_footer(container)

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=COLORS["input_bg"], background=COLORS["panel"])
        style.configure("Marine.Horizontal.TScale", background=COLORS["bg"], troughcolor=COLORS["panel"])
        style.configure("TCheckbutton", background=COLORS["panel"], foreground=COLORS["text"])

    def _build_header(self, parent: tk.Frame) -> None:
        header = tk.Frame(parent, bg=COLORS["bg"])
        header.pack(fill=tk.X, pady=(0, 12))

        tk.Label(
            header,
            text="ENGLISH  \U0001f1ec\U0001f1e7  \u2192  U.S. MARINE  \U0001f985\U0001f30e\u2693",
            font=("Segoe UI", 16, "bold"),
            fg=COLORS["gold"],
            bg=COLORS["bg"],
        ).pack(anchor=tk.W)

        tk.Label(
            header,
            text="Semper Translate — civilian speech degeneration engine",
            font=("Segoe UI", 10),
            fg=COLORS["text_dim"],
            bg=COLORS["bg"],
        ).pack(anchor=tk.W, pady=(4, 0))

    def _build_controls(self, parent: tk.Frame) -> None:
        controls = tk.Frame(parent, bg=COLORS["panel"], padx=12, pady=10)
        controls.pack(fill=tk.X, pady=(0, 10))

        row1 = tk.Frame(controls, bg=COLORS["panel"])
        row1.pack(fill=tk.X, pady=(0, 8))

        tk.Label(row1, text="Dictionary:", fg=COLORS["text"], bg=COLORS["panel"], font=("Segoe UI", 9)).pack(
            side=tk.LEFT
        )
        ttk.Combobox(
            row1,
            textvariable=self._mode_display_var,
            values=list(MODES.values()),
            state="readonly",
            width=20,
        ).pack(side=tk.LEFT, padx=(6, 16))

        tk.Label(row1, text="Fun mode:", fg=COLORS["text"], bg=COLORS["panel"], font=("Segoe UI", 9)).pack(
            side=tk.LEFT
        )
        ttk.Combobox(
            row1,
            textvariable=self._fun_display_var,
            values=list(FUN_MODES.values()),
            state="readonly",
            width=18,
        ).pack(side=tk.LEFT, padx=(6, 0))

        row2 = tk.Frame(controls, bg=COLORS["panel"])
        row2.pack(fill=tk.X, pady=(0, 8))

        tk.Label(row2, text="Rah density:", fg=COLORS["text"], bg=COLORS["panel"], font=("Segoe UI", 9)).pack(
            side=tk.LEFT
        )
        ttk.Scale(
            row2,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            variable=self._density_var,
            style="Marine.Horizontal.TScale",
            length=240,
        ).pack(side=tk.LEFT, padx=(6, 8))
        tk.Label(
            row2,
            textvariable=self._density_label_var,
            fg=COLORS["gold"],
            bg=COLORS["panel"],
            font=("Segoe UI", 9, "bold"),
            width=20,
            anchor=tk.W,
        ).pack(side=tk.LEFT)

        row3 = tk.Frame(controls, bg=COLORS["panel"])
        row3.pack(fill=tk.X)

        for name, value in DENSITY_PRESETS.items():
            self._mk_btn(row3, name, lambda v=value, n=name: self._set_density(v, n)).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Checkbutton(row3, text="Toxic barracks", variable=self._toxic_var).pack(side=tk.LEFT, padx=(12, 8))
        ttk.Checkbutton(row3, text="Live translate", variable=self._live_var).pack(side=tk.LEFT)

    def _build_examples(self, parent: tk.Frame) -> None:
        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.pack(fill=tk.X, pady=(0, 8))

        tk.Label(frame, text="Examples:", fg=COLORS["text_dim"], bg=COLORS["bg"], font=("Segoe UI", 8)).pack(
            anchor=tk.W
        )
        btn_row = tk.Frame(frame, bg=COLORS["bg"])
        btn_row.pack(fill=tk.X, pady=(2, 0))

        labels = ["Slippers", "Coffee", "Bathroom", "Bed", "Groceries", "In line", "Head/head"]
        for label, sentence in zip(labels, EXAMPLE_SENTENCES):
            self._mk_btn(btn_row, label, lambda s=sentence: self._load_example(s), small=True).pack(
                side=tk.LEFT, padx=(0, 4)
            )

    def _build_io_panels(self, parent: tk.Frame) -> None:
        io = tk.Frame(parent, bg=COLORS["bg"])
        io.pack(fill=tk.BOTH, expand=True)

        in_frame = tk.Frame(io, bg=COLORS["bg"])
        in_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 6))

        tk.Label(in_frame, text="CIVILIAN INPUT", fg=COLORS["text_dim"], bg=COLORS["bg"], font=("Segoe UI", 9)).pack(
            anchor=tk.W
        )
        self._input = tk.Text(
            in_frame,
            height=4,
            wrap=tk.WORD,
            bg=COLORS["input_bg"],
            fg=COLORS["text"],
            insertbackground=COLORS["gold"],
            relief=tk.FLAT,
            padx=10,
            pady=8,
            font=("Consolas", 11),
        )
        self._input.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        self._input.insert("1.0", EXAMPLE_SENTENCES[0])

        btn_row = tk.Frame(io, bg=COLORS["bg"])
        btn_row.pack(fill=tk.X, pady=6)

        self._mk_btn(btn_row, "\U0001f985 TRANSLATE", self._do_translate, accent=True).pack(side=tk.LEFT, padx=(0, 6))
        self._mk_btn(btn_row, "\U0001f3b2 RE-ROLL", self._do_reroll).pack(side=tk.LEFT, padx=(0, 6))
        self._mk_btn(btn_row, "\U0001f4cb COPY", self._copy_output).pack(side=tk.LEFT)

        stats = tk.Frame(io, bg=COLORS["bg"])
        stats.pack(fill=tk.X)
        tk.Label(stats, textvariable=self._confidence_var, fg=COLORS["gold"], bg=COLORS["bg"], font=("Segoe UI", 9, "bold")).pack(
            anchor=tk.W
        )
        tk.Label(stats, textvariable=self._stats_var, fg=COLORS["text_dim"], bg=COLORS["bg"], font=("Segoe UI", 8)).pack(
            anchor=tk.W, pady=(2, 0)
        )

        out_frame = tk.Frame(io, bg=COLORS["bg"])
        out_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        tk.Label(out_frame, text="MARINE OUTPUT", fg=COLORS["text_dim"], bg=COLORS["bg"], font=("Segoe UI", 9)).pack(
            anchor=tk.W
        )
        self._output = tk.Text(
            out_frame,
            height=4,
            wrap=tk.WORD,
            bg=COLORS["panel"],
            fg=COLORS["gold"],
            relief=tk.FLAT,
            padx=10,
            pady=8,
            font=("Consolas", 11),
            state=tk.DISABLED,
        )
        self._output.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

    def _build_breakdown(self, parent: tk.Frame) -> None:
        frame = tk.Frame(parent, bg=COLORS["bg"])
        frame.pack(fill=tk.BOTH, expand=False, pady=(8, 0))

        tk.Label(frame, text="WORD BREAKDOWN", fg=COLORS["text_dim"], bg=COLORS["bg"], font=("Segoe UI", 9)).pack(
            anchor=tk.W
        )
        self._breakdown = tk.Text(
            frame,
            height=5,
            wrap=tk.WORD,
            bg=COLORS["input_bg"],
            fg=COLORS["text_dim"],
            relief=tk.FLAT,
            padx=10,
            pady=6,
            font=("Consolas", 9),
            state=tk.DISABLED,
        )
        self._breakdown.pack(fill=tk.X, pady=(4, 0))

    def _build_footer(self, parent: tk.Frame) -> None:
        footer = tk.Frame(parent, bg=COLORS["bg"])
        footer.pack(fill=tk.X, pady=(10, 0))

        tk.Label(footer, text='"Semper Translate."', fg=COLORS["text_dim"], bg=COLORS["bg"], font=("Segoe UI", 9, "italic")).pack()
        tk.Label(
            footer,
            text="Moonshoes and knowledge sponges are not official USMC doctrine.",
            fg=COLORS["text_dim"],
            bg=COLORS["bg"],
            font=("Segoe UI", 8),
        ).pack(pady=(2, 0))

    def _mk_btn(
        self,
        parent: tk.Widget,
        text: str,
        command,
        *,
        accent: bool = False,
        small: bool = False,
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=COLORS["accent"] if accent else COLORS["button"],
            fg="white" if accent else COLORS["text"],
            activebackground="#a50000" if accent else COLORS["button_hover"],
            activeforeground="white" if accent else COLORS["text"],
            relief=tk.FLAT,
            padx=6 if small else 12,
            pady=2 if small else 6,
            font=("Segoe UI", 8 if small else 10, "bold" if accent else "normal"),
            cursor="hand2",
        )

    def _bind_events(self) -> None:
        self._mode_display_var.trace_add("write", self._on_mode_change)
        self._fun_display_var.trace_add("write", self._on_fun_change)
        self._density_var.trace_add("write", self._on_density_change)
        self._toxic_var.trace_add("write", lambda *_: self._schedule_live())
        self.bind("<Control-Return>", lambda _e: self._do_translate())
        self._input.bind("<Control-Return>", lambda _e: self._do_translate())
        self._input.bind("<KeyRelease>", lambda _e: self._schedule_live())

    def _on_mode_change(self, *_args: object) -> None:
        for key, label in MODES.items():
            if label == self._mode_display_var.get():
                self._mode_key_var.set(key)
                break
        self._schedule_live()

    def _on_fun_change(self, *_args: object) -> None:
        for key, label in FUN_MODES.items():
            if label == self._fun_display_var.get():
                self._fun_key_var.set(key)
                break
        self._schedule_live()

    def _on_density_change(self, *_args: object) -> None:
        value = int(float(self._density_var.get()))
        self._density_label_var.set(f"{self._density_label_for(value)} ({value}%)")
        self._schedule_live()

    def _density_label_for(self, value: int) -> str:
        if value >= 100:
            return "Sergeant Major"
        if value >= 90:
            return "Terminal Marine"
        if value >= 65:
            return "Staff NCO"
        if value >= 35:
            return "Boot"
        if value >= 10:
            return "Civilian"
        return "Poolie"

    def _set_density(self, value: int, name: str) -> None:
        self._density_var.set(value)
        self._density_label_var.set(f"{name} ({value}%)")

    def _load_example(self, sentence: str) -> None:
        self._input.delete("1.0", tk.END)
        self._input.insert("1.0", sentence)
        self._do_translate(new_seed=True)

    def _schedule_live(self) -> None:
        if not self._live_var.get():
            return
        if self._live_job:
            self.after_cancel(self._live_job)
        self._live_job = self.after(LIVE_DEBOUNCE_MS, self._do_translate)

    def _do_reroll(self) -> None:
        self._do_translate(new_seed=True)

    def _do_translate(self, new_seed: bool = False) -> None:
        if self._live_job:
            self.after_cancel(self._live_job)
            self._live_job = None

        text = self._input.get("1.0", tk.END)
        stripped = text.strip()

        if new_seed:
            seed = None
        elif stripped:
            seed = abs(hash(stripped)) % 1_000_000
        else:
            seed = None

        result = translate(
            text,
            mode=self._mode_key_var.get(),
            density=int(float(self._density_var.get())),
            fun_mode=self._fun_key_var.get(),
            toxic=self._toxic_var.get(),
            seed=seed,
        )
        self._last_seed = result.seed

        self._output.config(state=tk.NORMAL)
        self._output.delete("1.0", tk.END)
        self._output.insert("1.0", result.text)
        self._output.config(state=tk.DISABLED)

        self._breakdown.config(state=tk.NORMAL)
        self._breakdown.delete("1.0", tk.END)
        self._breakdown.insert("1.0", format_breakdown(result))
        self._breakdown.config(state=tk.DISABLED)

        self._confidence_var.set(f"Translation confidence: {result.confidence}%")
        self._stats_var.set(
            f"Readiness: {result.stats.readiness}  ·  Motivation: {result.stats.motivation}  ·  "
            f"Crayon level: {result.stats.crayon_level}  ·  Seed: {result.seed}"
        )

    def _copy_output(self) -> None:
        text = self._output.get("1.0", tk.END).strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self._stats_var.set("Copied to clipboard. " + self._stats_var.get())


def run() -> None:
    app = MarineTranslatorApp()
    app.mainloop()
