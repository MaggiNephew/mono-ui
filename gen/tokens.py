"""Load tokens/mono.json and resolve colour expressions.

A colour value can be:
  "#rrggbb" / "#rrggbbaa"     literal
  "gray.900"                   reference into the gray ramp
  "color.fg"                   reference to another role in the same variant
  "alpha(ref, 0.22)"           ref with that opacity
  "mix(refA, refB, 0.05)"      refA blended over refB, refA weighted 0.05
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int
    a: float = 1.0

    # ---- formats ----
    @property
    def hex(self) -> str:
        """#rrggbb, ignoring alpha."""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    @property
    def hex8(self) -> str:
        """#rrggbbaa."""
        return f"{self.hex}{round(self.a * 255):02x}"

    @property
    def argb8(self) -> str:
        """#aarrggbb (Qt / qt6ct order)."""
        return f"#{round(self.a * 255):02x}{self.r:02x}{self.g:02x}{self.b:02x}"

    @property
    def css(self) -> str:
        if self.a >= 1:
            return self.hex
        return f"rgba({self.r}, {self.g}, {self.b}, {fmt(self.a)})"

    @property
    def rgb_csv(self) -> str:
        return f"{self.r},{self.g},{self.b}"

    def floats(self) -> tuple[float, float, float, float]:
        return (self.r / 255, self.g / 255, self.b / 255, self.a)

    @property
    def opaque(self) -> bool:
        return self.a >= 1

    def over(self, base: "Color") -> "Color":
        """Flatten onto an opaque background."""
        a = self.a
        return Color(
            round(self.r * a + base.r * (1 - a)),
            round(self.g * a + base.g * (1 - a)),
            round(self.b * a + base.b * (1 - a)),
            1.0,
        )


def fmt(x: float) -> str:
    s = f"{x:.4f}".rstrip("0").rstrip(".")
    return s or "0"


def parse_hex(s: str) -> Color:
    h = s.lstrip("#")
    if len(h) == 6:
        return Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
    if len(h) == 8:
        return Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16) / 255)
    raise ValueError(f"bad hex colour {s!r}")


_FN = re.compile(r"^(alpha|mix)\((.*)\)$")


class Tokens:
    def __init__(self, path: Path | None = None):
        self.path = path or ROOT / "tokens" / "mono.json"
        self.data = json.loads(self.path.read_text())
        self.gray = {k: parse_hex(v) for k, v in self.data["gray"].items()}
        self.variants = list(self.data["variants"].keys())
        self._cache: dict[tuple[str | None, str], Color] = {}

    # ---- colour resolution ----
    def color(self, expr: str, variant: str | None = None, _depth: int = 0) -> Color:
        if _depth > 20:
            raise ValueError(f"reference loop at {expr!r}")
        key = (variant, expr)
        if key in self._cache:
            return self._cache[key]
        e = expr.strip()
        if e.startswith("#"):
            c = parse_hex(e)
        elif m := _FN.match(e):
            fn, args = m.group(1), [a.strip() for a in split_args(m.group(2))]
            if fn == "alpha":
                base = self.color(args[0], variant, _depth + 1)
                c = Color(base.r, base.g, base.b, float(args[1]))
            else:
                a = self.color(args[0], variant, _depth + 1)
                b = self.color(args[1], variant, _depth + 1)
                t = float(args[2])
                c = Color(round(a.r * t + b.r * (1 - t)), round(a.g * t + b.g * (1 - t)), round(a.b * t + b.b * (1 - t)))
        elif e.startswith("gray."):
            c = self.gray[e.split(".", 1)[1]]
        elif e.startswith("color."):
            if variant is None:
                raise ValueError(f"{expr!r} needs a variant")
            c = self.color(self.data["variants"][variant]["color"][e.split(".", 1)[1]], variant, _depth + 1)
        else:
            raise ValueError(f"can't resolve colour {expr!r}")
        self._cache[key] = c
        return c

    # ---- variant helpers ----
    def v(self, variant: str) -> dict:
        return self.data["variants"][variant]

    def roles(self, variant: str) -> dict[str, Color]:
        return {k: self.color(x, variant) for k, x in self.v(variant)["color"].items()}

    def solid(self, variant: str) -> dict[str, Color]:
        """Every role flattened over the variant background (for toolkits without alpha)."""
        roles = self.roles(variant)
        bg = roles["bg"]
        return {k: (c if c.opaque else c.over(bg)) for k, c in roles.items()}

    def terminal(self) -> dict:
        t = self.data["terminal"]
        out = {k: self.color(x) for k, x in t.items() if isinstance(x, str) and not k.startswith("$")}
        out["ansi"] = [self.color(x) for x in t["ansi"]]
        return out

    def syntax(self, variant: str | None = None) -> dict[str, dict]:
        """Code-highlighting roles: {"keyword": {"color": Color, "bold": True, ...}, ...}
        A variant can carry its own "syntax" table (paper does, since it's light)."""
        table = self.v(variant).get("syntax") if variant else None
        table = table or self.data["syntax"]
        out = {}
        for k, spec in table.items():
            if k.startswith("$"):
                continue
            out[k] = {"color": self.color(spec["color"]),
                      **{f: bool(spec.get(f)) for f in ("bold", "italic", "underline", "strikethrough")}}
        return out

    # ---- per-variant facts, so generators never check variant names ----
    def mode(self, variant: str) -> str:
        return self.v(variant).get("mode", "dark")

    def light(self, variant: str) -> bool:
        return self.mode(variant) == "light"

    def shade(self, variant: str, expr: str) -> Color:
        """A colour meant for a dark background; flipped (255 - value) on light variants."""
        c = self.color(expr, variant)
        if not self.light(variant):
            return c
        return Color(255 - c.r, 255 - c.g, 255 - c.b, c.a)

    FONT_FILES = {("Fraunces", 300): "Fraunces-Light.ttf", ("Fraunces", 400): "Fraunces-Regular.ttf",
                  ("Space Grotesk", 400): "SpaceGrotesk-Regular.ttf", ("Space Grotesk", 500): "SpaceGrotesk-Medium.ttf",
                  ("Space Mono", 400): "SpaceMono-Regular.ttf", ("Space Mono", 700): "SpaceMono-Bold.ttf",
                  ("3270 Nerd Font", 400): "3270NerdFont-Regular.ttf", ("3270 Nerd Font", 700): "3270NerdFont-Regular.ttf",
                  ("3270 Nerd Font Mono", 400): "3270NerdFontMono-Regular.ttf"}

    def font_files(self, variant: str) -> dict[str, str]:
        """TTF file name in fonts/ttf for each font role of a variant."""
        return {k: self.FONT_FILES[(f["family"], f["weight"])] for k, f in self.v(variant)["font"].items()}

    def app_px(self, variant: str) -> int:
        """Default desktop text size: 3270 reads small, so it gets one more pixel."""
        return self.v(variant)["size"]["ui"] + (2 if "3270" in self.v(variant)["font"]["sans"]["family"] else 1)

    def display_scale(self, variant: str) -> float:
        """Heading size relative to body text in desktop apps."""
        return 2.4 if self.serif_display(variant) else 1.9

    def title(self, variant: str) -> str:
        return f"Mono {variant.capitalize()}"

    def square_corners(self, variant: str) -> bool:
        return self.v(variant)["radius"]["md"] == 0

    def serif_display(self, variant: str) -> bool:
        """Display face differs from the UI face (Fraunces) -> headings get drawn bigger and tighter."""
        f = self.v(variant)["font"]
        return f["display"]["family"] != f["sans"]["family"]

    def term(self, variant: str) -> dict:
        """Terminal colours. round = your kitty exactly; square = website black; others override in tokens."""
        t = self.terminal()
        if variant == "round":
            return t
        over = self.v(variant).get("terminal", {})
        bg = self.color(over.get("background", "gray.50"))
        out = {**t, "background": bg, "backgroundAlt": bg, "tabActiveFg": bg}
        for k, x in over.items():
            if k == "ansi":
                out["ansi"] = [self.color(a) for a in x]
            elif k != "background":
                out[k] = self.color(x)
        return out

    def editor(self, variant: str) -> dict[str, Color]:
        """UI colours editors need, built from the variant roles."""
        c = self.solid(variant)
        sq = variant == "square"
        over = {k: self.color(x) for k, x in self.v(variant).get("editor", {}).items()}
        out = {
            "bg": c["bg"], "fg": self.color("gray.850"), "panel": c["bgAlt"] if sq else self.color("gray.50"),
            "surface": c["surface"], "raised": c["surfaceAlt"],
            "cursorLine": self.color("gray.75") if sq else self.color("gray.150"),
            "selection": c["selection"], "selectionFg": c["onSelection"], "search": self.color("gray.400"),
            "lineNr": c["fgFaint"], "lineNrActive": c["fg"], "border": c["line"], "borderStrong": c["lineStrong"],
            "indent": c["lineSoft"], "indentActive": c["line"], "cursor": c["fgStrong"],
            "muted": c["fgMuted"], "faint": c["fgFaint"], "strong": c["fgStrong"], "accent": c["accent"],
            "onAccent": c["onAccent"], "match": self.color("gray.300"),
        }
        out.update(over)
        return out

    def rice(self, section: str) -> dict:
        return {k: (self.color(x) if isinstance(x, str) else x) for k, x in self.data["rice"][section].items()}


def split_args(s: str) -> list[str]:
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    return out


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


HEADER = "generated by mono-ui from tokens/mono.json -- edit the tokens, not this file"
