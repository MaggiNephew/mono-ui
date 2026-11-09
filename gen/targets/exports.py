"""Plain token constants for any language: JSON, C/C++, Python, D, JS/TS, Lua, Rust, Go, C#.

Each export has both variants with every colour role (hex and 0-1 floats,
solid = flattened over the background), sizes, radii, borders and font names.
"""
from __future__ import annotations

import json
from pathlib import Path

from tokens import HEADER, Tokens, fmt, write


def resolved(t: Tokens) -> dict:
    out = {"name": t.data["name"], "version": t.data["version"], "gray": {k: c.hex for k, c in t.gray.items()},
           "space": t.data["space"], "motion": t.data["motion"], "variants": {}}
    for v in t.variants:
        d = t.v(v)
        roles, solid = t.roles(v), t.solid(v)
        out["variants"][v] = {
            "color": {k: c.css for k, c in roles.items()},
            "solid": {k: c.hex for k, c in solid.items()},
            "font": d["font"], "size": d["size"], "label": d["label"], "radius": d["radius"],
            "border": d["border"], "control": d["control"], "lineHeight": d["lineHeight"],
        }
    return out


def numbers(t: Tokens, v: str) -> list[tuple[str, int | float]]:
    d = t.v(v)
    nums: list[tuple[str, int | float]] = []
    for group in ("size", "radius", "border", "control"):
        for k, x in d[group].items():
            nums.append((f"{group}_{k}", x))
    nums.append(("line_height", d["lineHeight"]))
    return nums


def flt(x: float) -> str:
    s = fmt(x)
    return s if "." in s else s + ".0"


def snake(s: str) -> str:
    return "".join("_" + c.lower() if c.isupper() else c for c in s)


def build(t: Tokens, out: Path) -> list[Path]:
    o = out / "exports"
    files = []
    data = resolved(t)
    p = o / "mono.json"
    write(p, json.dumps(data, indent=2) + "\n")
    files.append(p)
    files.append(c_header(t, o))
    files.append(python(t, o))
    files.append(dlang(t, o))
    files += js(t, o, data)
    files.append(lua(t, o))
    files.append(rust(t, o))
    files.append(golang(t, o))
    files.append(csharp(t, o))
    return files


def c_header(t: Tokens, o: Path) -> Path:
    L = [f"/* {HEADER} */", "#ifndef MONO_TOKENS_H", "#define MONO_TOKENS_H", "",
         "/* Colours are 0xRRGGBB (solid, flattened over the variant background) plus 0xAARRGGBB where alpha matters. */", ""]
    for v in t.variants:
        V = v.upper()
        L.append(f"/* ---- {v} ---- */")
        roles, solid = t.roles(v), t.solid(v)
        for k in roles:
            L.append(f"#define MONO_{V}_{snake(k).upper():<14} 0x{solid[k].hex[1:]}u")
            if not roles[k].opaque:
                c = roles[k]
                L.append(f"#define MONO_{V}_{snake(k).upper() + '_ARGB':<14} 0x{round(c.a*255):02x}{c.hex[1:]}u")
        for k, x in numbers(t, v):
            L.append(f"#define MONO_{V}_{k.upper():<14} {x}")
        for k, f in t.v(v)["font"].items():
            L.append(f"#define MONO_{V}_FONT_{k.upper():<9} \"{f['family']}\"")
        L.append("")
    L.append("#endif")
    p = o / "c" / "mono_tokens.h"
    write(p, "\n".join(L) + "\n")
    return p


def python(t: Tokens, o: Path) -> Path:
    L = [f'"""{HEADER}"""', "", "from types import SimpleNamespace as _NS", ""]
    for v in t.variants:
        roles, solid = t.roles(v), t.solid(v)
        d = t.v(v)
        L.append(f"{v} = _NS(")
        L.append("    color=_NS(" + ", ".join(f"{snake(k)}={c.css!r}" for k, c in roles.items()) + "),")
        L.append("    solid=_NS(" + ", ".join(f"{snake(k)}={c.hex!r}" for k, c in solid.items()) + "),")
        L.append("    font=_NS(" + ", ".join(f"{k}={f['family']!r}" for k, f in d["font"].items()) + "),")
        for grp in ("size", "radius", "border", "control"):
            L.append(f"    {grp}=_NS(" + ", ".join(f"{snake(k)}={x}" for k, x in d[grp].items()) + "),")
        L.append(f"    line_height={d['lineHeight']},")
        L.append(")")
        L.append("")
    L.append("variants = {" + ", ".join(f"{v!r}: {v}" for v in t.variants) + "}")
    p = o / "python" / "mono_tokens.py"
    write(p, "\n".join(L) + "\n")
    return p


def dlang(t: Tokens, o: Path) -> Path:
    L = [f"// {HEADER}", "module monoui.tokens;", "",
         "/// A colour as 0-255 channels plus 0-1 alpha.", "struct Rgba { ubyte r, g, b; float a = 1; }", ""]
    for v in t.variants:
        roles, solid = t.roles(v), t.solid(v)
        d = t.v(v)
        L.append(f"/// {d['description']}")
        L.append(f"struct {v.capitalize()}")
        L.append("{")
        for k, c in roles.items():
            s = solid[k]
            L.append(f"    enum Rgba {k} = Rgba({c.r}, {c.g}, {c.b}, {fmt(c.a)}f);")
            L.append(f"    enum string {k}Hex = \"{s.hex}\";")
        for k, x in numbers(t, v):
            L.append(f"    enum {k} = {x};")
        for k, f in d["font"].items():
            L.append(f"    enum string font{k.capitalize()} = \"{f['family']}\";")
        L.append("}")
        L.append("")
    p = o / "d" / "monoui" / "tokens.d"
    write(p, "\n".join(L) + "\n")
    return p


def js(t: Tokens, o: Path, data: dict) -> list[Path]:
    body = json.dumps(data["variants"], indent=2)
    p1 = o / "js" / "mono-tokens.js"
    write(p1, f"// {HEADER}\nexport const variants = {body};\n" + "".join(f"export const {v} = variants.{v};\n" for v in t.variants) + "export default variants;\n")
    roles = list(t.roles("square").keys())
    p2 = o / "js" / "mono-tokens.d.ts"
    write(p2, f"""// {HEADER}
export type Role = {' | '.join(repr(r) for r in roles)};
export interface Font {{ family: string; weight: number; fallback: string }}
export interface Variant {{
  color: Record<Role, string>;
  solid: Record<Role, string>;
  font: {{ display: Font; sans: Font; strong: Font; mono: Font }};
  size: Record<string, number>;
  label: {{ uppercase: boolean; tracking: number; weight: number }};
  radius: {{ sm: number; md: number; lg: number; pill: number }};
  border: {{ width: number; focus: number }};
  control: {{ height: number; heightSmall: number; padX: number }};
  lineHeight: number;
}}
export declare const variants: {{ {"; ".join(f"{v}: Variant" for v in t.variants)} }};
{"".join(f"export declare const {v}: Variant;" + chr(10) for v in t.variants)}export default variants;
""")
    return [p1, p2]


def lua(t: Tokens, o: Path) -> Path:
    L = [f"-- {HEADER}", "local M = {}"]
    for v in t.variants:
        roles, solid = t.roles(v), t.solid(v)
        d = t.v(v)
        L.append(f"M.{v} = {{")
        L.append("  color = {" + ", ".join(f'{k} = "{c.css}"' for k, c in roles.items()) + "},")
        L.append("  solid = {" + ", ".join(f'{k} = "{c.hex}"' for k, c in solid.items()) + "},")
        L.append("  font = {" + ", ".join(f'{k} = "{f["family"]}"' for k, f in d["font"].items()) + "},")
        for grp in ("size", "radius", "border", "control"):
            L.append(f"  {grp} = {{" + ", ".join(f"{k} = {x}" for k, x in d[grp].items()) + "},")
        L.append("}")
    L.append("return M")
    p = o / "lua" / "mono_tokens.lua"
    write(p, "\n".join(L) + "\n")
    return p


def rust(t: Tokens, o: Path) -> Path:
    L = [f"// {HEADER}", "#![allow(dead_code)]", "",
         "#[derive(Clone, Copy, Debug, PartialEq)]", "pub struct Rgba { pub r: u8, pub g: u8, pub b: u8, pub a: f32 }", ""]
    for v in t.variants:
        roles, solid = t.roles(v), t.solid(v)
        L.append(f"pub mod {v} {{")
        L.append("    use super::Rgba;")
        for k, c in roles.items():
            L.append(f"    pub const {snake(k).upper()}: Rgba = Rgba {{ r: {c.r}, g: {c.g}, b: {c.b}, a: {flt(c.a)} }};")
            L.append(f"    pub const {snake(k).upper()}_HEX: &str = \"{solid[k].hex}\";")
        for k, x in numbers(t, v):
            ty = "f32" if isinstance(x, float) else "u32"
            val = f"{x}" if ty == "u32" else f"{x}_f32"
            L.append(f"    pub const {k.upper()}: {ty} = {val};")
        for k, f in t.v(v)["font"].items():
            L.append(f"    pub const FONT_{k.upper()}: &str = \"{f['family']}\";")
        L.append("}")
        L.append("")
    p = o / "rust" / "mono_tokens.rs"
    write(p, "\n".join(L) + "\n")
    return p


def golang(t: Tokens, o: Path) -> Path:
    L = [f"// {HEADER}", "package monotokens", "", "type Rgba struct{ R, G, B uint8; A float32 }", ""]
    for v in t.variants:
        roles, solid = t.roles(v), t.solid(v)
        V = v.capitalize()
        L.append(f"// {V} variant")
        L.append("var (")
        for k, c in roles.items():
            K = k[0].upper() + k[1:]
            L.append(f"\t{V}{K} = Rgba{{{c.r}, {c.g}, {c.b}, {fmt(c.a)}}}")
            L.append(f"\t{V}{K}Hex = \"{solid[k].hex}\"")
        for k, f in t.v(v)["font"].items():
            L.append(f"\t{V}Font{k.capitalize()} = \"{f['family']}\"")
        L.append(")")
        L.append("const (")
        for k, x in numbers(t, v):
            name = "".join(p.capitalize() for p in k.split("_"))
            L.append(f"\t{V}{name} = {x}")
        L.append(")")
        L.append("")
    p = o / "go" / "monotokens" / "tokens.go"
    write(p, "\n".join(L) + "\n")
    return p


def csharp(t: Tokens, o: Path) -> Path:
    L = [f"// {HEADER}", "namespace MonoUI;", "", "public readonly record struct Rgba(byte R, byte G, byte B, float A = 1f);", ""]
    for v in t.variants:
        roles, solid = t.roles(v), t.solid(v)
        L.append(f"public static class {v.capitalize()}")
        L.append("{")
        for k, c in roles.items():
            K = k[0].upper() + k[1:]
            L.append(f"    public static readonly Rgba {K} = new({c.r}, {c.g}, {c.b}, {fmt(c.a)}f);")
            L.append(f"    public const string {K}Hex = \"{solid[k].hex}\";")
        for k, x in numbers(t, v):
            name = "".join(p.capitalize() for p in k.split("_"))
            ty = "float" if isinstance(x, float) else "int"
            L.append(f"    public const {ty} {name} = {x}{'f' if ty == 'float' else ''};")
        for k, f in t.v(v)["font"].items():
            L.append(f"    public const string Font{k.capitalize()} = \"{f['family']}\";")
        L.append("}")
        L.append("")
    p = o / "csharp" / "MonoTokens.cs"
    write(p, "\n".join(L) + "\n")
    return p
