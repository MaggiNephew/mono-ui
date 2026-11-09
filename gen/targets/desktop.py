"""Desktop extras: GTK 4 / libadwaita, Waybar, Rofi, Fuzzel, Wofi, Dunst, Mako, btop, Firefox, Vencord."""
from __future__ import annotations

from pathlib import Path

from tokens import HEADER, Tokens, write


def build(t: Tokens, out: Path) -> list[Path]:
    o = out / "desktop"
    files: list[Path] = []
    for v in t.variants:
        c, d = t.solid(v), t.v(v)
        r = d["radius"]
        # the rice uses the Mono cut of 3270 in bars and launchers
        font = d["font"]["mono" if "3270" in d["font"]["sans"]["family"] else "sans"]["family"]
        files += [gtk4(t, o, v, c, r), waybar(o, v, c, r, font), rofi(o, v, c, r, font), fuzzel(o, v, c, r, font),
                  wofi(o, v, c, r, font), dunst(o, v, c, r, font), mako(o, v, c, r, font), btop(t, o, v, c),
                  firefox(o, v, c, r), vencord(o, v, c, r, d, t.light(v))]
    return files


def gtk4(t: Tokens, o: Path, v: str, c: dict, r: dict) -> Path:
    named = {
        "accent_color": c["fgStrong"], "accent_bg_color": c["accent"], "accent_fg_color": c["onAccent"],
        "destructive_color": c["fgStrong"], "destructive_bg_color": c["surfaceAlt"], "destructive_fg_color": c["fgStrong"],
        "success_color": c["fg"], "success_bg_color": c["surfaceAlt"], "success_fg_color": c["fg"],
        "warning_color": c["fgDim"], "warning_bg_color": c["surfaceAlt"], "warning_fg_color": c["fg"],
        "error_color": c["fgStrong"], "error_bg_color": c["surfaceAlt"], "error_fg_color": c["fgStrong"],
        "window_bg_color": c["bg"], "window_fg_color": c["fg"], "view_bg_color": c["bgAlt"], "view_fg_color": c["fg"],
        "headerbar_bg_color": c["bg"], "headerbar_fg_color": c["fg"], "headerbar_border_color": c["line"],
        "headerbar_backdrop_color": c["bg"], "headerbar_shade_color": c["lineSoft"],
        "sidebar_bg_color": c["bgAlt"], "sidebar_fg_color": c["fg"], "sidebar_backdrop_color": c["bgAlt"],
        "sidebar_shade_color": c["lineSoft"], "card_bg_color": c["surface"], "card_fg_color": c["fg"],
        "card_shade_color": c["line"], "dialog_bg_color": c["surface"], "dialog_fg_color": c["fg"],
        "popover_bg_color": c["surface"], "popover_fg_color": c["fg"], "popover_shade_color": c["line"],
        "thumbnail_bg_color": c["surface"], "thumbnail_fg_color": c["fg"], "shade_color": c["lineSoft"],
        "scrollbar_outline_color": c["bg"],
        # GTK 4 (non-libadwaita) names
        "theme_bg_color": c["bg"], "theme_fg_color": c["fg"], "theme_base_color": c["bgAlt"],
        "theme_text_color": c["fg"], "theme_selected_bg_color": c["selection"], "theme_selected_fg_color": c["onSelection"],
        "borders": c["line"],
    }
    rounded = r["md"] > 0
    css = [f"/* Mono {v} for GTK 4 and libadwaita. Put in ~/.config/gtk-4.0/gtk.css  ({HEADER}) */"]
    css += [f"@define-color {k} {x.hex};" for k, x in named.items()]
    css += [
        "",
        f"button, entry, spinbutton, dropdown > button, combobox > button {{ border-radius: {r['md']}px; }}",
        f"button {{ border: 1px solid {c['lineStrong'].hex}; box-shadow: none; }}",
        f"button.flat, headerbar button, .linked > button {{ border-color: transparent; }}",
        f"button.suggested-action {{ background: {c['accent'].hex}; color: {c['onAccent'].hex}; border-color: {c['accent'].hex}; }}",
        f"button.destructive-action {{ background: transparent; color: {c['fgStrong'].hex}; border: 1px dashed {c['fg'].hex}; }}",
        f"entry {{ background: {c['bgAlt'].hex}; border: 1px solid {c['line'].hex}; box-shadow: none; }}",
        f"entry:focus-within {{ border-color: {c['focus'].hex}; outline: none; }}",
        f".card, list.boxed-list {{ border-radius: {r['lg']}px; border: 1px solid {c['line'].hex}; box-shadow: none; }}",
        f"popover > contents, window.dialog, messagedialog {{ border-radius: {r['lg']}px; }}",
        f"check {{ border-radius: {4 if rounded else 0}px; }}",
        f"switch, switch > slider {{ border-radius: {r['pill'] if rounded else 0}px; }}",
        f"scale > trough > slider {{ border-radius: {7 if rounded else 0}px; }}",
        f"progressbar > trough, progressbar > trough > progress {{ border-radius: {2 if rounded else 0}px; }}",
        f"window {{ border-radius: {r['lg']}px; }}" if rounded else "window, window.csd { border-radius: 0; }",
        f"*:focus-visible {{ outline-color: {c['focus'].hex}; }}",
        f"selection {{ background: {c['selection'].hex}; color: {c['onSelection'].hex}; }}",
    ]
    p = o / "gtk4" / f"mono-{v}.css"
    write(p, "\n".join(css) + "\n")
    return p


def waybar(o: Path, v: str, c: dict, r: dict, font: str) -> Path:
    pill = r["md"]
    css = f"""/* Mono {v} for Waybar: @import "mono-{v}.css"; in style.css  ({HEADER}) */
* {{ font-family: "{font}", monospace; font-size: 13px; min-height: 0; }}
window#waybar {{ background: {c['bgAlt'].hex}; color: {c['fg'].hex}; border-bottom: 1px solid {c['line'].hex}; }}
tooltip {{ background: {c['surface'].hex}; border: 1px solid {c['lineStrong'].hex}; border-radius: {r['sm']}px; }}
tooltip label {{ color: {c['fg'].hex}; }}
#workspaces {{ margin: 4px; }}
#workspaces button {{ padding: 0 8px; margin: 0 2px; color: {c['fgFaint'].hex}; background: transparent;
  border: 1px solid transparent; border-radius: {pill}px; box-shadow: none; }}
#workspaces button:hover {{ color: {c['fg'].hex}; background: {c['surface'].hex}; border-color: {c['line'].hex}; }}
#workspaces button.active, #workspaces button.focused {{ color: {c['onAccent'].hex}; background: {c['accent'].hex}; border-color: {c['accent'].hex}; }}
#workspaces button.urgent {{ color: {c['fgStrong'].hex}; border: 1px dashed {c['fgStrong'].hex}; }}
#clock, #cpu, #memory, #network, #pulseaudio, #wireplumber, #battery, #backlight, #tray, #mpris, #custom-media,
#bluetooth, #temperature, #idle_inhibitor, #privacy, #language, #window {{
  padding: 0 10px; margin: 4px 2px; color: {c['fgDim'].hex}; background: transparent;
  border: 1px solid {c['line'].hex}; border-radius: {pill}px; }}
#window {{ border-color: transparent; color: {c['fgMuted'].hex}; }}
#clock {{ color: {c['fg'].hex}; font-weight: bold; }}
#battery.warning, #battery.critical, #network.disconnected, #pulseaudio.muted, #wireplumber.muted {{
  color: {c['fgStrong'].hex}; border-style: dashed; border-color: {c['fg'].hex}; }}
#privacy-item {{ color: {c['onAccent'].hex}; background: {c['accent'].hex}; border-radius: {pill}px; padding: 0 6px; }}
#tray > .needs-attention {{ border-bottom: 1px solid {c['fgStrong'].hex}; }}
"""
    p = o / "waybar" / f"mono-{v}.css"
    write(p, css)
    return p


def rofi(o: Path, v: str, c: dict, r: dict, font: str) -> Path:
    rasi = f"""/* Mono {v} for rofi: rofi -theme mono-{v}.rasi  ({HEADER}) */
* {{
    bg: {c['bg'].hex};  bg-alt: {c['surface'].hex};  fg: {c['fg'].hex};  fg-dim: {c['fgMuted'].hex};
    line: {c['line'].hex};  strong: {c['lineStrong'].hex};  accent: {c['accent'].hex};  on-accent: {c['onAccent'].hex};
    background-color: transparent;
    text-color: @fg;
    font: "{font} 12";
}}
window {{ width: 640px; background-color: @bg; border: 1px; border-color: @strong; border-radius: {r['lg']}px; padding: 14px; }}
mainbox {{ spacing: 10px; children: [ inputbar, listview ]; }}
inputbar {{ background-color: @bg-alt; border: 1px; border-color: @line; border-radius: {r['md']}px; padding: 8px 10px; spacing: 8px;
    children: [ prompt, entry ]; }}
prompt {{ text-color: @fg-dim; }}
entry {{ placeholder: "Search"; placeholder-color: @fg-dim; cursor: text; }}
listview {{ lines: 8; spacing: 2px; scrollbar: false; }}
element {{ padding: 7px 10px; border-radius: {r['sm']}px; spacing: 10px; }}
element normal.normal, element alternate.normal {{ background-color: transparent; text-color: @fg; }}
element selected.normal {{ background-color: @accent; text-color: @on-accent; }}
element-icon {{ size: 18px; }}
element-text {{ text-color: inherit; highlight: bold; }}
message {{ border: 1px; border-color: @line; border-radius: {r['md']}px; padding: 8px; }}
"""
    p = o / "rofi" / f"mono-{v}.rasi"
    write(p, rasi)
    return p


def fuzzel(o: Path, v: str, c: dict, r: dict, font: str) -> Path:
    a = lambda x: x.hex[1:] + "ff"
    ini = f"""# Mono {v} for fuzzel: include=~/.config/fuzzel/mono-{v}.ini  ({HEADER})
[main]
font={font}:size=12
[colors]
background={a(c['bg'])}
text={a(c['fg'])}
prompt={a(c['fgMuted'])}
placeholder={a(c['fgFaint'])}
input={a(c['fgStrong'])}
match={a(c['fgStrong'])}
selection={a(c['accent'])}
selection-text={a(c['onAccent'])}
selection-match={a(c['onAccent'])}
counter={a(c['fgFaint'])}
border={a(c['lineStrong'])}
[border]
width=1
radius={r['lg']}
"""
    p = o / "fuzzel" / f"mono-{v}.ini"
    write(p, ini)
    return p


def wofi(o: Path, v: str, c: dict, r: dict, font: str) -> Path:
    css = f"""/* Mono {v} for wofi: wofi --style mono-{v}.css  ({HEADER}) */
* {{ font-family: "{font}", monospace; font-size: 13px; }}
window {{ background-color: {c['bg'].hex}; border: 1px solid {c['lineStrong'].hex}; border-radius: {r['lg']}px; }}
#outer-box {{ padding: 12px; }}
#input {{ background: {c['surface'].hex}; color: {c['fg'].hex}; border: 1px solid {c['line'].hex}; border-radius: {r['md']}px;
  padding: 6px 10px; box-shadow: none; margin-bottom: 8px; }}
#input:focus {{ border-color: {c['focus'].hex}; }}
#inner-box, #scroll {{ background: transparent; }}
#entry {{ padding: 6px 10px; border-radius: {r['sm']}px; color: {c['fg'].hex}; }}
#entry:selected {{ background: {c['accent'].hex}; outline: none; }}
#entry:selected #text {{ color: {c['onAccent'].hex}; }}
#text {{ color: {c['fg'].hex}; }}
"""
    p = o / "wofi" / f"mono-{v}.css"
    write(p, css)
    return p


def dunst(o: Path, v: str, c: dict, r: dict, font: str) -> Path:
    conf = f"""# Mono {v} for dunst: copy into ~/.config/dunst/dunstrc.d/  ({HEADER})
[global]
    font = "{font} 11"
    frame_width = 1
    frame_color = "{c['lineStrong'].hex}"
    separator_color = frame
    corner_radius = {r['lg']}
    padding = 10
    horizontal_padding = 12
    highlight = "{c['fg'].hex}"
    progress_bar_frame_width = 0
    progress_bar_corner_radius = {2 if r['md'] else 0}

[urgency_low]
    background = "{c['bg'].hex}"
    foreground = "{c['fgMuted'].hex}"
    frame_color = "{c['line'].hex}"

[urgency_normal]
    background = "{c['bg'].hex}"
    foreground = "{c['fg'].hex}"
    frame_color = "{c['lineStrong'].hex}"

[urgency_critical]
    background = "{c['accent'].hex}"
    foreground = "{c['onAccent'].hex}"
    frame_color = "{c['accent'].hex}"
"""
    p = o / "dunst" / f"mono-{v}.conf"
    write(p, conf)
    return p


def mako(o: Path, v: str, c: dict, r: dict, font: str) -> Path:
    conf = f"""# Mono {v} for mako: include=~/.config/mako/mono-{v}  ({HEADER})
font={font} 11
background-color={c['bg'].hex}
text-color={c['fg'].hex}
border-color={c['lineStrong'].hex}
border-size=1
border-radius={r['lg']}
padding=10,12
progress-color=over {c['surfaceAlt'].hex}

[urgency=low]
text-color={c['fgMuted'].hex}
border-color={c['line'].hex}

[urgency=critical]
background-color={c['accent'].hex}
text-color={c['onAccent'].hex}
border-color={c['accent'].hex}
"""
    p = o / "mako" / f"mono-{v}"
    write(p, conf)
    return p


def btop(t: Tokens, o: Path, v: str, c: dict) -> Path:
    g = lambda k: t.shade(v, f"gray.{k}").hex
    keys = {
        "main_bg": c["bg"].hex, "main_fg": c["fg"].hex, "title": c["fgStrong"].hex, "hi_fg": c["fgStrong"].hex,
        "selected_bg": c["selection"].hex, "selected_fg": c["onSelection"].hex, "inactive_fg": c["fgFaint"].hex,
        "graph_text": c["fgMuted"].hex, "meter_bg": c["lineSoft"].hex, "proc_misc": c["fgDim"].hex,
        "cpu_box": c["line"].hex, "mem_box": c["line"].hex, "net_box": c["line"].hex, "proc_box": c["line"].hex,
        "div_line": c["lineSoft"].hex,
        "temp_start": g("550"), "temp_mid": g("800"), "temp_end": g("1000"),
        "cpu_start": g("550"), "cpu_mid": g("800"), "cpu_end": g("1000"),
        "free_start": g("400"), "free_mid": g("650"), "free_end": g("850"),
        "cached_start": g("400"), "cached_mid": g("650"), "cached_end": g("850"),
        "available_start": g("400"), "available_mid": g("650"), "available_end": g("850"),
        "used_start": g("550"), "used_mid": g("800"), "used_end": g("1000"),
        "download_start": g("400"), "download_mid": g("700"), "download_end": g("1000"),
        "upload_start": g("400"), "upload_mid": g("700"), "upload_end": g("1000"),
        "process_start": g("550"), "process_mid": g("800"), "process_end": g("1000"),
    }
    lines = [f"# Mono {v} for btop: copy to ~/.config/btop/themes/ and pick it in the options menu  ({HEADER})"]
    lines += [f'theme[{k}]="{x}"' for k, x in keys.items()]
    p = o / "btop" / f"mono-{v}.theme"
    write(p, "\n".join(lines) + "\n")
    return p


def firefox(o: Path, v: str, c: dict, r: dict) -> Path:
    css = f"""/* Mono {v} for Firefox. Put in <profile>/chrome/userChrome.css and set
   toolkit.legacyUserProfileCustomizations.stylesheets = true in about:config.  ({HEADER}) */
:root {{
  --toolbar-bgcolor: {c['bg'].hex} !important;
  --toolbar-color: {c['fg'].hex} !important;
  --toolbar-field-background-color: {c['surface'].hex} !important;
  --toolbar-field-color: {c['fg'].hex} !important;
  --toolbar-field-focus-background-color: {c['bgAlt'].hex} !important;
  --toolbar-field-focus-border-color: {c['focus'].hex} !important;
  --toolbar-field-border-color: {c['line'].hex} !important;
  --lwt-accent-color: {c['bgAlt'].hex} !important;
  --lwt-text-color: {c['fgMuted'].hex} !important;
  --tab-selected-bgcolor: {c['surface'].hex} !important;
  --tab-selected-textcolor: {c['fgStrong'].hex} !important;
  --tab-border-radius: {r['md']}px !important;
  --toolbarbutton-border-radius: {r['sm']}px !important;
  --arrowpanel-background: {c['surface'].hex} !important;
  --arrowpanel-color: {c['fg'].hex} !important;
  --arrowpanel-border-color: {c['lineStrong'].hex} !important;
  --arrowpanel-border-radius: {r['lg']}px !important;
  --sidebar-background-color: {c['bgAlt'].hex} !important;
  --sidebar-text-color: {c['fg'].hex} !important;
  --chrome-content-separator-color: {c['line'].hex} !important;
  --focus-outline-color: {c['focus'].hex} !important;
  --button-primary-bgcolor: {c['accent'].hex} !important;
  --button-primary-color: {c['onAccent'].hex} !important;
  --urlbarView-highlight-background: {c['selection'].hex} !important;
}}
#navigator-toolbox {{ border-bottom: 1px solid {c['line'].hex} !important; }}
.tab-background[selected] {{ outline: 1px solid {c['lineStrong'].hex} !important; box-shadow: none !important; }}
"""
    p = o / "firefox" / f"userChrome-{v}.css"
    write(p, css)
    return p


def vencord(o: Path, v: str, c: dict, r: dict, d: dict, light: bool = False) -> Path:
    font = d["font"]["sans"]["family"]
    mono_font = d["font"]["mono"]["family"]
    css = f"""/**
 * @name Mono {v.capitalize()}
 * @author MaggiNephew
 * @description {"White and black" if light else "Black and white"} Discord, from mono-ui ({v} variant).{" Use it with Discord's light theme." if light else ""}
 * @version 1.0.0
 * @source https://github.com/MaggiNephew/mono-ui
 */
/* {HEADER} */
{".theme-light, " if light else ""}.theme-dark, .theme-darker, .theme-midnight, :root {{
  /* older Discord variables */
  --background-primary: {c['bg'].hex};
  --background-secondary: {c['bgAlt'].hex};
  --background-secondary-alt: {c['bgAlt'].hex};
  --background-tertiary: {c['bgAlt'].hex};
  --background-floating: {c['surface'].hex};
  --background-modifier-hover: {c['surface'].hex};
  --background-modifier-active: {c['surfaceAlt'].hex};
  --background-modifier-selected: {c['selection'].hex};
  --background-modifier-accent: {c['line'].hex};
  --channeltextarea-background: {c['surface'].hex};
  --text-normal: {c['fg'].hex};
  --text-muted: {c['fgMuted'].hex};
  --header-primary: {c['fgStrong'].hex};
  --header-secondary: {c['fgMuted'].hex};
  --interactive-normal: {c['fgMuted'].hex};
  --interactive-hover: {c['fg'].hex};
  --interactive-active: {c['fgStrong'].hex};
  --interactive-muted: {c['fgFaint'].hex};
  --channels-default: {c['fgMuted'].hex};
  --text-link: {c['fgStrong'].hex};
  --brand-experiment: {c['accent'].hex};
  --brand-500: {c['accent'].hex};
  --button-filled-brand-background: {c['accent'].hex};
  --button-filled-brand-text: {c['onAccent'].hex};
  --scrollbar-thin-thumb: {c['lineStrong'].hex};
  --scrollbar-auto-thumb: {c['lineStrong'].hex};
  --scrollbar-auto-track: transparent;
  /* 2025 visual refresh variables */
  --background-base-lowest: {c['bgAlt'].hex};
  --background-base-lower: {c['bgAlt'].hex};
  --background-base-low: {c['bg'].hex};
  --background-surface-high: {c['surface'].hex};
  --background-surface-higher: {c['surfaceAlt'].hex};
  --background-surface-highest: {c['surfaceAlt'].hex};
  --text-default: {c['fg'].hex};
  --text-strong: {c['fgStrong'].hex};
  --text-subtle: {c['fgMuted'].hex};
  --border-subtle: {c['lineSoft'].hex};
  --border-normal: {c['line'].hex};
  --border-strong: {c['lineStrong'].hex};
  --font-primary: "{font}", sans-serif;
  --font-display: "{font}", sans-serif;
  --font-code: "{mono_font}", monospace;
  --radius-sm: {r['sm']}px;
  --radius-md: {r['md']}px;
  --radius-lg: {r['lg']}px;
}}
/* keep role colours, but drop the brand blurple everywhere else */
[class*="mention"] {{ background: {c['surfaceAlt'].hex} !important; color: {c['fgStrong'].hex} !important; }}
"""
    p = o / "vencord" / f"mono-{v}.theme.css"
    write(p, css)
    return p
