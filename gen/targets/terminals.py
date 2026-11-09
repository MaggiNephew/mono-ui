"""Terminals: kitty, foot, Alacritty, WezTerm, Ghostty, tmux, Xresources, Windows Terminal. Every variant.

round = your kitty colours exactly (background #0d0d12); square = the website black #0a0a0a;
blend and paper set their own in tokens (paper is light, with the ANSI greys flipped).
"""
from __future__ import annotations

import json
from pathlib import Path

from tokens import HEADER, Tokens, write

NAMES = ["black", "red", "green", "yellow", "blue", "magenta", "cyan", "white"]


def build(t: Tokens, out: Path) -> list[Path]:
    o = out / "terminals"
    files: list[Path] = []
    wt = []
    for v in t.variants:
        c = t.term(v)
        a = c["ansi"]
        h = lambda x: x.hex
        bar = t.solid(v)

        files.append(_w(o / "kitty" / f"mono-{v}.conf", [f"# Mono {v} for kitty: include mono-{v}.conf  ({HEADER})",
            f"background {h(c['background'])}", f"foreground {h(c['foreground'])}",
            *[f"color{i} {h(x)}" for i, x in enumerate(a)],
            f"selection_foreground {h(c['selectionFg'])}", f"selection_background {h(c['selectionBg'])}",
            f"cursor {h(c['cursor'])}", f"cursor_text_color {h(c['cursorText'])}",
            f"url_color {h(t.shade(v, 'gray.1000'))}", f"active_border_color {h(bar['focus'])}",
            f"inactive_border_color {h(bar['line'])}", f"tab_bar_background {h(c['background'])}",
            f"active_tab_background {h(c['tabActiveBg'])}", f"active_tab_foreground {h(c['tabActiveFg'])}",
            f"inactive_tab_background {h(c['tabInactiveBg'])}", f"inactive_tab_foreground {h(c['tabInactiveFg'])}"]))

        files.append(_w(o / "foot" / f"mono-{v}.ini", [f"# Mono {v} for foot: include=~/.config/foot/mono-{v}.ini  ({HEADER})",
            "[colors-dark]",  # foot's default theme section, whatever the brightness
            f"background={h(c['backgroundAlt'])[1:]}", f"foreground={h(c['foreground'])[1:]}",
            *[f"regular{i}={h(x)[1:]}" for i, x in enumerate(a[:8])],
            *[f"bright{i}={h(x)[1:]}" for i, x in enumerate(a[8:])],
            f"selection-foreground={h(c['selectionFg'])[1:]}", f"selection-background={h(c['selectionBg'])[1:]}"]))

        files.append(_w(o / "alacritty" / f"mono-{v}.toml", [f"# Mono {v} for Alacritty. 0.14+: [general] import = [\"~/.config/alacritty/mono-{v}.toml\"]; older: import = [...] at the top.  ({HEADER})",
            "[colors.primary]", f'background = "{h(c["background"])}"', f'foreground = "{h(c["foreground"])}"',
            f'bright_foreground = "{h(t.shade(v, "gray.1000"))}"', f'dim_foreground = "{h(t.shade(v, "gray.650"))}"', "",
            "[colors.cursor]", f'text = "{h(c["cursorText"])}"', f'cursor = "{h(c["cursor"])}"', "",
            "[colors.selection]", f'text = "{h(c["selectionFg"])}"', f'background = "{h(c["selectionBg"])}"', "",
            "[colors.normal]", *[f'{n} = "{h(x)}"' for n, x in zip(NAMES, a[:8])], "",
            "[colors.bright]", *[f'{n} = "{h(x)}"' for n, x in zip(NAMES, a[8:])]]))

        files.append(_w(o / "wezterm" / f"mono-{v}.lua", [f"-- Mono {v} for WezTerm. {HEADER}",
            f"-- local mono = dofile(wezterm.config_dir .. \"/mono-{v}.lua\");  config.colors = mono",
            "return {", f'  foreground = "{h(c["foreground"])}",', f'  background = "{h(c["background"])}",',
            f'  cursor_bg = "{h(c["cursor"])}",', f'  cursor_fg = "{h(c["cursorText"])}",', f'  cursor_border = "{h(c["cursor"])}",',
            f'  selection_fg = "{h(c["selectionFg"])}",', f'  selection_bg = "{h(c["selectionBg"])}",',
            f'  split = "{h(bar["line"])}",',
            "  ansi = { " + ", ".join(f'"{h(x)}"' for x in a[:8]) + " },",
            "  brights = { " + ", ".join(f'"{h(x)}"' for x in a[8:]) + " },",
            "  tab_bar = {", f'    background = "{h(c["background"])}",',
            f'    active_tab = {{ bg_color = "{h(c["tabActiveBg"])}", fg_color = "{h(c["tabActiveFg"])}" }},',
            f'    inactive_tab = {{ bg_color = "{h(c["tabInactiveBg"])}", fg_color = "{h(c["tabInactiveFg"])}" }},',
            f'    inactive_tab_hover = {{ bg_color = "{h(bar["surfaceAlt"])}", fg_color = "{h(bar["fg"])}" }},',
            f'    new_tab = {{ bg_color = "{h(c["background"])}", fg_color = "{h(bar["fgMuted"])}" }},',
            "  },", "}"]))

        files.append(_w(o / "ghostty" / f"mono-{v}", [f"# Mono {v} for Ghostty: copy to ~/.config/ghostty/themes/ and set theme = mono-{v}  ({HEADER})",
            f"background = {h(c['background'])}", f"foreground = {h(c['foreground'])}",
            f"cursor-color = {h(c['cursor'])}", f"cursor-text = {h(c['cursorText'])}",
            f"selection-background = {h(c['selectionBg'])}", f"selection-foreground = {h(c['selectionFg'])}",
            *[f"palette = {i}={h(x)}" for i, x in enumerate(a)]]))

        files.append(_w(o / "tmux" / f"mono-{v}.conf", [f"# Mono {v} for tmux: source-file ~/.config/tmux/mono-{v}.conf  ({HEADER})",
            f'set -g status-style "bg={h(bar["bgAlt"] if v == "round" else c["background"])},fg={h(bar["fgMuted"])}"',
            f'set -g status-left-style "bg={h(bar["accent"])},fg={h(bar["onAccent"])},bold"',
            f'set -g status-left " #S "',
            f'set -g status-right-style "fg={h(bar["fgMuted"])}"',
            f'set -g status-right " %H:%M "',
            f'set -g window-status-format " #I #W "',
            f'set -g window-status-current-format " #I #W "',
            f'set -g window-status-style "fg={h(bar["fgFaint"])}"',
            f'set -g window-status-current-style "bg={h(bar["surface"])},fg={h(bar["fgStrong"])},bold"',
            f'set -g pane-border-style "fg={h(bar["line"])}"',
            f'set -g pane-active-border-style "fg={h(bar["focus"])}"',
            f'set -g message-style "bg={h(bar["surface"])},fg={h(bar["fg"])}"',
            f'set -g message-command-style "bg={h(bar["surface"])},fg={h(bar["fg"])}"',
            f'set -g mode-style "bg={h(bar["selection"])},fg={h(bar["onSelection"])}"',
            f'set -g display-panes-active-colour "{h(bar["fgStrong"])}"',
            f'set -g display-panes-colour "{h(bar["fgFaint"])}"',
            f'set -g clock-mode-colour "{h(bar["fg"])}"']))

        files.append(_w(o / "xresources" / f"mono-{v}.Xresources", [f"! Mono {v}: xrdb -merge mono-{v}.Xresources  ({HEADER})",
            f"*.background: {h(c['background'])}", f"*.foreground: {h(c['foreground'])}", f"*.cursorColor: {h(c['cursor'])}",
            *[f"*.color{i}: {h(x)}" for i, x in enumerate(a)]]))

        wnames = ["black", "red", "green", "yellow", "blue", "purple", "cyan", "white"]
        scheme = {"name": f"Mono {v.capitalize()}", "background": h(c["background"]), "foreground": h(c["foreground"]),
                  "cursorColor": h(c["cursor"]), "selectionBackground": h(c["selectionBg"])}
        for i, x in enumerate(a):
            n = wnames[i % 8]
            scheme[("bright" + n.capitalize()) if i >= 8 else n] = h(x)
        wt.append(scheme)
    p = o / "windows-terminal" / "mono-schemes.json"
    write(p, json.dumps({"$comment": f"Add these to \"schemes\" in Windows Terminal settings.json. {HEADER}", "schemes": wt}, indent=2) + "\n")
    files.append(p)
    return files


def _w(p: Path, lines: list[str]) -> Path:
    write(p, "\n".join(lines) + "\n")
    return p
