"""Textual (Python terminal UIs): two Themes plus a stylesheet.

    from mono_textual import MonoApp       # or register_themes(app)
    class MyApp(MonoApp): ...
    MyApp(variant="round").run()

Terminals can't do corner radius or typefaces, so the variants differ by border style:
square = thin solid lines, round = rounded "round" borders (like your bar's pills).
"""
from __future__ import annotations

import json
from pathlib import Path

from tokens import HEADER, Tokens, write

TCSS = """/* mono-ui for Textual -- {header}
   Classes: .h1 .label .muted .faint .card .stats .cell, Button.-fill/.-line/.-ghost */

Screen {{ background: $background; color: $foreground; }}

/* ---------- type ---------- */
.h1 {{ color: $mono-fg; text-style: bold; }}
.label {{ color: $mono-fg-muted; text-style: {label_style}; }}
.muted {{ color: $mono-fg-muted; }}
.faint {{ color: $mono-fg-faint; }}

/* ---------- containers ---------- */
.card {{ background: $mono-surface; border: {border} $mono-line; padding: 0 1; height: auto; }}
.stats {{ border: {border} $mono-line; height: auto; }}
.cell {{ border-right: {cell_border} $mono-line; padding: 0 1; width: 1fr; height: auto; }}
.cell:last-child {{ border-right: none; }}
.cell .value {{ color: $mono-fg; text-style: bold; }}

/* ---------- buttons ---------- */
Button {{
  background: $background; color: $mono-fg; border: {border} $mono-fg; height: 3; min-width: 10;
  text-style: {label_style}; tint: transparent;
}}
Button:hover {{ background: $mono-surface; border: {border} $mono-fg-strong; }}
Button:focus {{ text-style: {label_style}; background-tint: transparent; }}
Button.-fill {{ background: $mono-accent; color: $mono-on-accent; border: {border} $mono-accent; }}
Button.-fill:hover {{ background: $mono-accent-hover; border: {border} $mono-accent-hover; }}
Button.-line {{ border: {border} $mono-line-strong; }}
Button.-ghost {{ border: {border} $background; color: $mono-fg-muted; }}
Button.-ghost:hover {{ color: $mono-fg; border: {border} $mono-surface; }}
Button:disabled {{ color: $mono-disabled; border: {border} $mono-line; background: $background; }}

/* ---------- inputs ---------- */
Input, Select > SelectCurrent, TextArea {{ background: $mono-bg-alt; color: $mono-fg; border: {border} $mono-line; }}
Input:focus, Select:focus > SelectCurrent, TextArea:focus {{ border: {border} $mono-focus; }}
Input > .input--placeholder {{ color: $mono-fg-faint; }}
Checkbox, RadioButton {{ background: transparent; border: none; color: $mono-fg; }}
Switch {{ background: transparent; border: {border} $mono-line; }}
Switch:focus {{ border: {border} $mono-focus; }}
ProgressBar Bar > .bar--bar {{ color: $mono-fg; background: $mono-line-soft; }}
ProgressBar Bar > .bar--complete {{ color: $mono-fg-strong; }}

/* ---------- tabs, tables, lists ---------- */
Tabs {{ background: $background; }}
Tab {{ color: $mono-fg-muted; text-style: {label_style}; }}
Tab.-active {{ color: $mono-fg; }}
Underline > .underline--bar {{ color: $mono-fg; background: $mono-line; }}
DataTable {{ background: $mono-bg-alt; border: {border} $mono-line; }}
DataTable > .datatable--header {{ background: $mono-bg-alt; color: $mono-fg-muted; text-style: {label_style}; }}
DataTable > .datatable--cursor {{ background: $mono-selection; color: $mono-on-selection; }}
ListView, OptionList {{ background: $mono-bg-alt; border: {border} $mono-line; }}
ListView > ListItem.-highlight, OptionList > .option-list--option-highlighted {{ background: $mono-selection; color: $mono-on-selection; }}
Header {{ background: $mono-bg-alt; color: $mono-fg; }}
Footer {{ background: $mono-bg-alt; }}
Footer .footer-key--key {{ background: $mono-surface-alt; color: $mono-fg; }}
Footer .footer-key--description {{ color: $mono-fg-muted; }}
Log, RichLog {{ background: $mono-bg-alt; border: {border} $mono-line-soft; color: $mono-fg-dim; }}
"""


def kebab(s: str) -> str:
    return "".join("-" + c.lower() if c.isupper() else c for c in s)


def build(t: Tokens, out: Path) -> list[Path]:
    o = out / "textual"
    files = []
    themes = {}
    for v in t.variants:
        c = t.solid(v)
        border = "solid" if t.v(v)["radius"]["md"] == 0 else "round"
        label_style = "none"
        tcss = TCSS.format(header=HEADER, border=border, cell_border="solid" if border == "solid" else "vkey",
                           label_style=label_style)
        p = o / f"mono-{v}.tcss"
        write(p, tcss)
        files.append(p)
        themes[v] = {
            "name": f"mono-{v}",
            "primary": c["fg"].hex, "secondary": c["fgMuted"].hex, "accent": c["fgStrong"].hex,
            "foreground": c["fgDim"].hex, "background": c["bg"].hex, "surface": c["surface"].hex,
            "panel": c["surfaceAlt"].hex, "boost": c["surfaceAlt"].hex,
            "warning": c["fgStrong"].hex, "error": c["fgStrong"].hex, "success": c["fg"].hex,
            "dark": not t.light(v),
            "variables": {f"mono-{kebab(k)}": col.hex for k, col in c.items()} | {
                "block-cursor-background": c["fg"].hex, "block-cursor-foreground": c["onAccent"].hex,
                "block-cursor-text-style": "none", "footer-key-foreground": c["fg"].hex,
                "input-selection-background": c["selection"].hex, "scrollbar": c["lineStrong"].hex,
                "scrollbar-hover": c["fgMuted"].hex, "scrollbar-active": c["fg"].hex,
                "scrollbar-background": c["bgAlt"].hex, "scrollbar-corner-color": c["bgAlt"].hex,
                "border": c["focus"].hex, "border-blurred": c["line"].hex,
            },
        }
    tcss_by_variant = {v: (o / f"mono-{v}.tcss").read_text() for v in t.variants}
    mod = f'''"""mono-ui for Textual. {HEADER}

    from mono_textual import MonoApp
    class Demo(MonoApp):
        def compose(self): ...
    Demo(variant="round").run()       # or "square", "blend", "paper"

Or with your own App subclass: register_themes(app); app.theme = "mono-round"; and put
mono_textual.CSS["round"] in your App.CSS.
"""
from __future__ import annotations

import json

from textual.app import App
from textual.theme import Theme

_THEMES = json.loads(r"""{json.dumps(themes, indent=1)}""")
CSS = json.loads(r"""{json.dumps(tcss_by_variant)}""")
VARIANTS = tuple(_THEMES)


def themes() -> list[Theme]:
    return [Theme(**spec) for spec in _THEMES.values()]


def register_themes(app: App) -> None:
    for theme in themes():
        app.register_theme(theme)


class MonoApp(App):
    """An App with the mono theme and stylesheet applied. Switch with app.set_variant("square")."""

    CSS = CSS["round"]

    def __init__(self, *args, variant: str = "round", **kwargs):
        if variant not in VARIANTS:
            raise ValueError(f"variant must be one of {{VARIANTS}}")
        cls = type(self)
        if "_mono_user_css" not in cls.__dict__:
            # keep the subclass's own CSS and put the mono stylesheet in front of it
            cls._mono_user_css = cls.__dict__.get("CSS", "") if cls is not MonoApp else ""
        cls.CSS = CSS[variant] + "\\n" + cls._mono_user_css
        super().__init__(*args, **kwargs)
        self.variant = variant
        register_themes(self)
        self.theme = f"mono-{{variant}}"
'''
    p = o / "mono_textual.py"
    write(p, mod)
    files.append(p)
    return files
