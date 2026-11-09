"""Web frameworks on top of mono.css: Tailwind (v4 and v3), SCSS, React components.

Everything points at the --m-* CSS variables, so data-mono="square|round|blend|paper" still switches
the variant at runtime, including Tailwind utilities like bg-mono-surface or rounded-mono-md.
"""
from __future__ import annotations

import json
from pathlib import Path

from tokens import HEADER, ROOT, Tokens, write

REACT = ROOT / "gen" / "templates" / "react"


def kebab(s: str) -> str:
    return "".join("-" + c.lower() if c.isupper() else c for c in s)


def build(t: Tokens, out: Path) -> list[Path]:
    o = out / "webext"
    roles = list(t.roles("square").keys())
    sizes = list(t.v("square")["size"].keys())
    files = []

    # ---- Tailwind v4: CSS-first theme ----
    v4 = [f"/* mono-ui for Tailwind CSS v4. {HEADER}",
          "   @import \"tailwindcss\"; @import \"../web/mono.css\"; @import \"./mono.tailwind.css\";",
          "   Then: bg-mono-surface text-mono-fg border-mono-line rounded-mono-md font-mono-display ... */",
          "@theme inline {"]
    v4 += [f"  --color-mono-{kebab(r)}: var(--m-{kebab(r)});" for r in roles]
    v4 += [f"  --font-mono-{k}: var(--m-font-{k});" for k in ("display", "sans", "strong", "mono")]
    v4 += [f"  --text-mono-{k}: var(--m-size-{k});" for k in sizes]
    v4 += [f"  --radius-mono-{k}: var(--m-r-{k});" for k in ("sm", "md", "lg", "pill")]
    v4 += ["  --tracking-mono-label: var(--m-label-tracking);",
           "  --height-mono-control: var(--m-control-h);", "}"]
    p = o / "tailwind" / "mono.tailwind.css"
    write(p, "\n".join(v4) + "\n")
    files.append(p)

    # ---- Tailwind v3: preset ----
    preset = {
        "theme": {"extend": {
            "colors": {"mono": {kebab(r): f"var(--m-{kebab(r)})" for r in roles}},
            "fontFamily": {f"mono-{k}": f"var(--m-font-{k})" for k in ("display", "sans", "strong", "mono")},
            "fontSize": {f"mono-{k}": f"var(--m-size-{k})" for k in sizes},
            "borderRadius": {f"mono-{k}": f"var(--m-r-{k})" for k in ("sm", "md", "lg", "pill")},
            "letterSpacing": {"mono-label": "var(--m-label-tracking)"},
            "height": {"mono-control": "var(--m-control-h)"},
        }}
    }
    p = o / "tailwind" / "mono.preset.js"
    write(p, f"// mono-ui preset for Tailwind CSS v3: presets: [require(\"./mono.preset.js\")]. {HEADER}\n"
             f"module.exports = {json.dumps(preset, indent=2)};\n")
    files.append(p)

    # ---- SCSS ----
    sc = [f"// mono-ui for Sass. {HEADER}", "// @use \"mono\" as m;  then m.$square, m.color(fg), @include m.label;", "",
          "@use \"sass:map\";", ""]
    for v in t.variants:
        d = t.v(v)
        sc.append(f"${v}: (")
        sc += [f"  \"{kebab(k)}\": {c.css}," for k, c in t.roles(v).items()]
        sc += [f"  \"font-{k}\": (\"{f['family']}\", {f['fallback']})," for k, f in d["font"].items()]
        sc += [f"  \"size-{k}\": {x}px," for k, x in d["size"].items()]
        sc += [f"  \"radius-{k}\": {x}px," for k, x in d["radius"].items()]
        sc += [f"  \"control-height\": {d['control']['height']}px,", f"  \"label-tracking\": {d['label']['tracking']}em,",
               f"  \"label-uppercase\": {str(d['label']['uppercase']).lower()},"]
        sc.append(");")
        sc.append("")
    sc += [
        "/// Live value that follows data-mono (uses the CSS variables from mono.css).",
        "@function color($role) { @return var(--m-#{$role}); }",
        "@function size($name) { @return var(--m-size-#{$name}); }",
        "@function radius($name) { @return var(--m-r-#{$name}); }",
        "", "/// Static value from one variant, for when you can't use CSS variables.",
        "@function static($variant, $key) {",
        *[f"  @if $variant == {v} {{ @return map.get(${v}, $key); }}" for v in t.variants[1:]],
        f"  @return map.get(${t.variants[0]}, $key);",
        "}",
        "", "@mixin label {",
        "  font-family: var(--m-font-strong); font-weight: var(--m-label-weight); font-size: var(--m-size-label);",
        "  letter-spacing: var(--m-label-tracking); text-transform: var(--m-label-transform); color: var(--m-fg-muted);",
        "}", "", "@mixin surface($strong: false) {",
        "  background: var(--m-surface); border: 1px solid var(--m-line); border-radius: var(--m-r-lg);",
        "  @if $strong { border-color: var(--m-line-strong); }", "}", "", "@mixin hairline($side: bottom) { border-#{$side}: 1px solid var(--m-line-soft); }", ""]
    p = o / "scss" / "_mono.scss"
    write(p, "\n".join(sc))
    files.append(p)

    # ---- React (TypeScript, no dependencies besides react) ----
    for f in sorted(REACT.glob("*")):
        dst = o / "react" / f.name
        write(dst, f.read_text())
        files.append(dst)
    return files
