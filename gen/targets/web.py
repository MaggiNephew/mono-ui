"""Web: dist/web/mono.css (variables for both variants + components), fonts, mono.js."""
from __future__ import annotations

import shutil
from pathlib import Path

from tokens import HEADER, ROOT, Tokens, fmt, write

TEMPLATES = ROOT / "gen" / "templates" / "web"


def kebab(s: str) -> str:
    return "".join("-" + c.lower() if c.isupper() else c for c in s)


def font_stack(f: dict) -> str:
    return f"\"{f['family']}\", {f['fallback']}"


def variables(t: Tokens, v: str) -> list[str]:
    d = t.v(v)
    out = [f"  /* {d['description']} */"]
    for k, c in t.roles(v).items():
        out.append(f"  --m-{kebab(k)}: {c.css};")
    for k, f in d["font"].items():
        out.append(f"  --m-font-{k}: {font_stack(f)};")
    out.append(f"  --m-w-display: {d['font']['display']['weight']};")
    out.append(f"  --m-w-strong: {d['font']['strong']['weight']};")
    for k, x in d["size"].items():
        out.append(f"  --m-size-{k}: {x}px;")
    lab = d["label"]
    out.append(f"  --m-label-transform: {'uppercase' if lab['uppercase'] else 'none'};")
    out.append(f"  --m-label-tracking: {fmt(lab['tracking'])}em;")
    out.append(f"  --m-label-weight: {lab['weight']};")
    # buttons track a little less than labels; display type is tighter on the serif
    out.append(f"  --m-btn-tracking: {fmt(lab['tracking'] * 0.64)}em;")
    out.append(f"  --m-display-tracking: {'-0.03em' if t.serif_display(v) else '0'};")
    out.append(f"  --m-color-scheme: {t.mode(v)};")
    r = d["radius"]
    for k in ("sm", "md", "lg"):
        out.append(f"  --m-r-{k}: {r[k]}px;")
    out.append(f"  --m-r-pill: {r['pill']}px;")
    round_bits = "50%" if r["md"] > 0 else "0"
    out.append(f"  --m-r-thumb: {round_bits};")
    out.append(f"  --m-r-dot: {round_bits};")
    out.append(f"  --m-border: {d['border']['width']}px;")
    out.append(f"  --m-border-focus: {d['border']['focus']}px;")
    c = d["control"]
    out.append(f"  --m-control-h: {c['height']}px;")
    out.append(f"  --m-control-h-sm: {c['heightSmall']}px;")
    out.append(f"  --m-control-px: {c['padX']}px;")
    out.append(f"  --m-lh: {d['lineHeight']};")
    return out


def build(t: Tokens, out: Path) -> list[Path]:
    o = out / "web"
    shared = [f"  --m-s-{k}: {x}px;" for k, x in t.data["space"].items()]
    m = t.data["motion"]
    shared += [f"  --m-ease: cubic-bezier({', '.join(fmt(x) for x in m['ease'])});",
               f"  --m-fast: {m['fast']}ms;", f"  --m-base: {m['base']}ms;", f"  --m-slow: {m['slow']}ms;"]

    css = [f"/* mono-ui {t.data['version']} -- {HEADER}",
           "   Usage: <link rel=\"stylesheet\" href=\"mono.css\"> and <html data-mono=\"square\"> (or round, blend, paper).",
           "   Variants can be mixed: put data-mono on any element to switch that subtree. */", ""]
    css.append(fonts_css())
    css.append(":root, [data-mono] {")
    css += shared
    css.append("}")
    for i, v in enumerate(t.variants):
        css.append((":root, " if i == 0 else "") + f"[data-mono=\"{v}\"] {{")
        css += variables(t, v)
        css.append("}")
    css.append("")
    css.append((TEMPLATES / "components.css").read_text())

    p = o / "mono.css"
    write(p, "\n".join(css))
    files = [p]

    # fonts
    fonts_out = o / "fonts"
    fonts_out.mkdir(parents=True, exist_ok=True)
    for f in sorted((ROOT / "fonts" / "woff2").glob("*.woff2")):
        shutil.copy2(f, fonts_out / f.name)
        files.append(fonts_out / f.name)

    js = o / "mono.js"
    shutil.copy2(TEMPLATES / "mono.js", js)
    files.append(js)
    return files


def fonts_css() -> str:
    faces = [
        ("Fraunces", "Fraunces-Light", 300, "normal"),
        ("Fraunces", "Fraunces-LightItalic", 300, "italic"),
        ("Fraunces", "Fraunces-Regular", 400, "normal"),
        ("Space Grotesk", "SpaceGrotesk-Regular", 400, "normal"),
        ("Space Grotesk", "SpaceGrotesk-Medium", 500, "normal"),
        ("Space Mono", "SpaceMono-Regular", 400, "normal"),
        ("Space Mono", "SpaceMono-Bold", 700, "normal"),
    ]
    out = []
    for fam, file, w, style in faces:
        out.append(f"@font-face {{ font-family: \"{fam}\"; src: url(\"fonts/{file}.woff2\") format(\"woff2\"); "
                   f"font-weight: {w}; font-style: {style}; font-display: swap; }}")
    # 3270: small text file always, the large Nerd Font icon file only when an icon glyph is on the page
    text_range = "U+0020-024F, U+2000-206F, U+2190-21FF, U+2500-259F"
    icon_range = "U+E000-F8FF, U+F0000-F1AEF"
    for fam, base in (("3270 Nerd Font", "3270NerdFont-Regular"), ("3270 Nerd Font Mono", "3270NerdFontMono-Regular")):
        out.append(f"@font-face {{ font-family: \"{fam}\"; src: local(\"{fam}\"), url(\"fonts/{base}-text.woff2\") format(\"woff2\"); "
                   f"unicode-range: {text_range}; font-display: swap; }}")
        out.append(f"@font-face {{ font-family: \"{fam}\"; src: local(\"{fam}\"), url(\"fonts/{base}-icons.woff2\") format(\"woff2\"); "
                   f"unicode-range: {icon_range}; font-display: swap; }}")
    return "\n".join(out) + "\n"
