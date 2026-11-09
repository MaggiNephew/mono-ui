"""Qt: stylesheets + palette + icons, wrapped as a Python module (PySide6/PyQt6) and a C++ header.

dist/qt/mono-square.qss, mono-round.qss       raw stylesheets (icons referenced as mono:<name>.svg)
dist/qt/icons/<variant>/*.svg                 the indicator/arrow icons
dist/qt/python/mono_qt.py                      self-contained: apply(app, "round")
dist/qt/cpp/mono_qt.hpp                        self-contained, header-only: monoui::apply(app, monoui::Round)
"""
from __future__ import annotations

import json
from pathlib import Path
from string import Template

from tokens import HEADER, ROOT, Tokens, write

TEMPLATE = ROOT / "gen" / "templates" / "qt" / "mono.qss"

# QPalette role -> token role
PALETTE = {
    "Window": "bg", "WindowText": "fg", "Base": "bgAlt", "AlternateBase": "surface", "ToolTipBase": "surfaceAlt",
    "ToolTipText": "fg", "PlaceholderText": "fgFaint", "Text": "fg", "Button": "surface", "ButtonText": "fg",
    "BrightText": "fgStrong", "Light": "surfaceAlt", "Midlight": "surface", "Mid": "line", "Dark": "bgAlt",
    "Shadow": "bgAlt", "Highlight": "selection", "HighlightedText": "onSelection", "Link": "fgStrong",
    "LinkVisited": "fgDim",
}
PALETTE_DISABLED = {"WindowText": "disabled", "Text": "disabled", "ButtonText": "disabled", "HighlightedText": "fgMuted"}


def snake(s: str) -> str:
    return "".join("_" + c.lower() if c.isupper() else c for c in s)


def qss_values(t: Tokens, v: str) -> dict[str, str]:
    d = t.v(v)
    vals: dict[str, str] = {"variant": v}
    for k, c in t.solid(v).items():
        vals[snake(k)] = c.hex
    for k, f in d["font"].items():
        vals[f"font_{k}"] = f["family"]
    vals["w_display"] = str(d["font"]["display"]["weight"])
    vals["w_strong"] = str(d["font"]["strong"]["weight"])
    vals["label_weight"] = str(d["label"]["weight"])
    for k, x in d["size"].items():
        vals[f"size_{k}"] = str(x)
    s = d["size"]
    # desktop apps don't need the web's poster sizes: h1 is capped at 48px
    vals["size_h2"] = str(min(s["h2"], 48))
    vals["h2_qt"] = str(round((min(s["h2"], 48) + s["h3"]) / 2))
    r = d["radius"]
    rounded = r["md"] > 0
    vals.update(r_sm=str(r["sm"]), r_md=str(r["md"]), r_lg=str(r["lg"]),
                r_check=str(4 if rounded else 0), r_radio="8", r_thumb=str(7 if rounded else 0),
                r_bar=str(2 if rounded else 0), r_scroll=str(4 if rounded else 0))
    vals["border_focus"] = str(d["border"]["focus"])
    vals["control_inner"] = str(d["control"]["height"] - 2)
    vals["control_px"] = str(d["control"]["padX"])
    return vals


def icons(t: Tokens, v: str) -> dict[str, str]:
    c = t.solid(v)
    sq = t.v(v)["radius"]["md"] == 0
    stroke = "square" if sq else "round"
    check = lambda col: (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M3.5 8.5l3 3 6-7" fill="none" '
                         f'stroke="{col}" stroke-width="2" stroke-linecap="{stroke}" stroke-linejoin="{"miter" if sq else "round"}"/></svg>')
    chev = lambda d: (f'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 10 10"><path d="{d}" fill="none" stroke="{c["fgMuted"].hex}" '
                      f'stroke-width="1.5" stroke-linecap="{stroke}"/></svg>')
    dot = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><rect x="4.5" y="4.5" width="7" height="7" rx="3.5" '
           f'fill="{c["fgStrong"].hex}"/></svg>')
    return {
        "check.svg": check(c["onAccent"].hex),
        "check-fg.svg": check(c["fg"].hex),
        "dash.svg": (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16"><path d="M4 8h8" stroke="{c["onAccent"].hex}" '
                     f'stroke-width="2" stroke-linecap="{stroke}"/></svg>'),
        "radio.svg": dot,
        "chevron-down.svg": chev("M2 3.5l3 3 3-3"),
        "chevron-up.svg": chev("M2 6.5l3-3 3 3"),
    }


def palette(t: Tokens, v: str) -> dict:
    c = t.solid(v)
    return {"active": {r: c[k].hex for r, k in PALETTE.items()},
            "disabled": {r: c[k].hex for r, k in PALETTE_DISABLED.items()}}


def build(t: Tokens, out: Path) -> list[Path]:
    o = out / "qt"
    tpl = Template(TEMPLATE.read_text())
    files: list[Path] = []
    bundle = {}
    for v in t.variants:
        qss = tpl.substitute(qss_values(t, v))
        p = o / f"mono-{v}.qss"
        write(p, f"/* {HEADER} */\n" + qss)
        files.append(p)
        ic = icons(t, v)
        for name, svg in ic.items():
            ip = o / "icons" / v / name
            write(ip, svg + "\n")
            files.append(ip)
        d = t.v(v)
        bundle[v] = {
            "qss": qss, "icons": ic, "palette": palette(t, v),
            "font": {k: f["family"] for k, f in d["font"].items()},
            "size": d["size"], "label": d["label"],
        }
    files.append(python_module(t, o, bundle))
    files.append(cpp_header(t, o, bundle))
    return files


# ---------------------------------------------------------------- Python

def python_module(t: Tokens, o: Path, bundle: dict) -> Path:
    data = json.dumps(bundle, indent=1)
    text = f'''"""mono-ui for Qt (PySide6 or PyQt6). {HEADER}

    from mono_qt import apply, role, kind
    app = QApplication([])
    apply(app, "round")            # or "square", "blend", "paper"
    role(QLabel("Settings"), "h2")
    kind(QPushButton("Save"), "fill")

Fonts: if the families aren't installed, apply() loads the TTFs from mono-ui/fonts/ttf
(found next to this file, or set MONO_UI_FONTS=/path/to/fonts/ttf).
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

try:
    from PySide6.QtCore import QDir
    from PySide6.QtGui import QColor, QFont, QFontDatabase, QPalette
    from PySide6.QtWidgets import QApplication, QStyleFactory, QWidget
except ImportError:  # PyQt6
    from PyQt6.QtCore import QDir
    from PyQt6.QtGui import QColor, QFont, QFontDatabase, QPalette
    from PyQt6.QtWidgets import QApplication, QStyleFactory, QWidget

VARIANTS = {tuple(t.variants)!r}
_DATA = json.loads(r"""{data}""")


def _font_dirs():
    env = os.environ.get("MONO_UI_FONTS")
    if env:
        yield Path(env)
    here = Path(__file__).resolve()
    for up in here.parents:
        cand = up / "fonts" / "ttf"
        if cand.is_dir():
            yield cand
            break


def load_fonts() -> list[str]:
    """Register bundled TTFs for any family that isn't installed. Returns the families loaded."""
    have = set(QFontDatabase.families())
    loaded = []
    for d in _font_dirs():
        for f in sorted(d.glob("*.ttf")):
            ident = QFontDatabase.addApplicationFont(str(f))
            if ident >= 0:
                loaded += [fam for fam in QFontDatabase.applicationFontFamilies(ident) if fam not in have]
        break
    return loaded


def _icon_dir(variant: str) -> str:
    d = Path(tempfile.gettempdir()) / f"mono-ui-icons-{{os.getuid() if hasattr(os, 'getuid') else 0}}" / variant
    d.mkdir(parents=True, exist_ok=True)
    for name, svg in _DATA[variant]["icons"].items():
        p = d / name
        if not p.exists() or p.read_text() != svg:
            p.write_text(svg)
    return str(d)


def palette(variant: str = "round") -> QPalette:
    pal = QPalette()
    p = _DATA[variant]["palette"]
    for role, hexv in p["active"].items():
        r = getattr(QPalette.ColorRole, role)
        pal.setColor(QPalette.ColorGroup.Active, r, QColor(hexv))
        pal.setColor(QPalette.ColorGroup.Inactive, r, QColor(hexv))
        pal.setColor(QPalette.ColorGroup.Disabled, r, QColor(hexv))
    for role, hexv in p["disabled"].items():
        pal.setColor(QPalette.ColorGroup.Disabled, getattr(QPalette.ColorRole, role), QColor(hexv))
    return pal


def stylesheet(variant: str = "round") -> str:
    return _DATA[variant]["qss"]


def apply(app: QApplication, variant: str = "round", *, fonts: bool = True) -> None:
    """Theme the whole application."""
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {{VARIANTS}}")
    if fonts:
        load_fonts()
    QDir.setSearchPaths("mono", [_icon_dir(variant)])
    app.setStyle(QStyleFactory.create("Fusion"))
    app.setPalette(palette(variant))
    d = _DATA[variant]
    f = QFont(d["font"]["sans"])
    f.setPixelSize(d["size"]["ui"])
    app.setFont(f)
    app.setStyleSheet(stylesheet(variant))
    app.setProperty("monoVariant", variant)


def role(widget: QWidget, name: str) -> QWidget:
    """Mark a widget with a role from the stylesheet (h1, h2, h3, label, muted, faint, mono, stat, card, rule...)."""
    widget.setProperty("role", name)
    if name == "label":
        app = QApplication.instance()
        variant = (app.property("monoVariant") if app else None) or "round"
        lab = _DATA[variant]["label"]
        f = QFont(widget.font())
        if lab["uppercase"]:
            f.setCapitalization(QFont.Capitalization.AllUppercase)
        f.setLetterSpacing(QFont.SpacingType.PercentageSpacing, 100 + lab["tracking"] * 100)
        widget.setFont(f)
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    return widget


def kind(button: QWidget, name: str) -> QWidget:
    """Button style: "fill", "line" or "ghost" (default is outline)."""
    button.setProperty("kind", name)
    button.style().unpolish(button)
    button.style().polish(button)
    return button
'''
    p = o / "python" / "mono_qt.py"
    write(p, text)
    return p


# ---------------------------------------------------------------- C++

def cpp_str(s: str) -> str:
    # Raw string literal; the delimiter never appears in QSS/SVG.
    return f'R"MONO({s})MONO"'


def cpp_header(t: Tokens, o: Path, bundle: dict) -> Path:
    parts = [f"""// mono-ui for Qt 6 / C++17. {HEADER}
//
//   #include "mono_qt.hpp"
//   QApplication app(argc, argv);
//   monoui::apply(app, monoui::Variant::Round);          // or Square, Blend, Paper
//   monoui::setRole(titleLabel, "h2");
//   monoui::setKind(saveButton, "fill");
//
// Fonts: if the families aren't installed, apply() loads every .ttf from the directory
// you pass, or from $MONO_UI_FONTS.
#pragma once

#include <QApplication>
#include <QColor>
#include <QDir>
#include <QFile>
#include <QFont>
#include <QFontDatabase>
#include <QPalette>
#include <QStandardPaths>
#include <QStyle>
#include <QStyleFactory>
#include <QWidget>

namespace monoui {{

enum class Variant {{ {', '.join(v.capitalize() for v in t.variants)} }};

namespace detail {{
struct Icon {{ const char* name; const char* svg; }};
struct Role {{ QPalette::ColorRole role; const char* hex; }};
struct Data {{
    const char* name;
    const char* qss;
    const Icon* icons; int iconCount;
    const Role* palette; int paletteCount;
    const Role* disabled; int disabledCount;
    const char* fontSans; int uiPx;
    bool labelUpper; double labelTracking;
}};
"""]
    for v in t.variants:
        b = bundle[v]
        parts.append(f"inline const Icon icons_{v}[] = {{")
        for name, svg in b["icons"].items():
            parts.append(f"    {{\"{name}\", {cpp_str(svg)}}},")
        parts.append("};")
        parts.append(f"inline const Role palette_{v}[] = {{")
        for role, hexv in b["palette"]["active"].items():
            parts.append(f"    {{QPalette::{role}, \"{hexv}\"}},")
        parts.append("};")
        parts.append(f"inline const Role disabled_{v}[] = {{")
        for role, hexv in b["palette"]["disabled"].items():
            parts.append(f"    {{QPalette::{role}, \"{hexv}\"}},")
        parts.append("};")
        parts.append(f"inline const char qss_{v}[] = {cpp_str(b['qss'])};")
        lab = b["label"]
        parts.append(
            f"inline const Data data_{v} = {{\"{v}\", qss_{v}, icons_{v}, {len(b['icons'])}, palette_{v}, "
            f"{len(b['palette']['active'])}, disabled_{v}, {len(b['palette']['disabled'])}, \"{b['font']['sans']}\", "
            f"{b['size']['ui']}, {'true' if lab['uppercase'] else 'false'}, {lab['tracking']}}};")
        parts.append("")
    parts.append("inline const Data& data(Variant v) {\n    switch (v) {\n"
                 + "".join(f"        case Variant::{v.capitalize()}: return data_{v};\n" for v in t.variants)
                 + f"    }}\n    return data_{t.variants[0]};\n}}\n\n"
                 + "inline const Data& data(const QString& name) {\n"
                 + "".join(f"    if (name == \"{v}\") return data_{v};\n" for v in t.variants)
                 + "    return data_round;\n}\n")
    parts.append("""

inline QString iconDir(const Data& d) {
    QString base = QStandardPaths::writableLocation(QStandardPaths::CacheLocation);
    if (base.isEmpty()) base = QDir::tempPath();
    QDir dir(base + "/mono-ui-icons/" + d.name);
    dir.mkpath(".");
    for (int i = 0; i < d.iconCount; ++i) {
        QFile f(dir.filePath(d.icons[i].name));
        const QByteArray svg(d.icons[i].svg);
        if (f.open(QIODevice::ReadOnly) && f.readAll() == svg) continue;
        f.close();
        if (f.open(QIODevice::WriteOnly | QIODevice::Truncate)) f.write(svg);
    }
    return dir.absolutePath();
}
}  // namespace detail

/// Register the bundled TTFs (mono-ui/fonts/ttf) for families that aren't installed.
inline void loadFonts(QString dir = {}) {
    if (dir.isEmpty()) dir = qEnvironmentVariable("MONO_UI_FONTS");
    if (dir.isEmpty()) return;
    const QDir d(dir);
    for (const QString& f : d.entryList({"*.ttf"}, QDir::Files)) QFontDatabase::addApplicationFont(d.filePath(f));
}

inline QPalette palette(Variant v) {
    const auto& d = detail::data(v);
    QPalette pal;
    for (int i = 0; i < d.paletteCount; ++i)
        for (auto g : {QPalette::Active, QPalette::Inactive, QPalette::Disabled})
            pal.setColor(g, d.palette[i].role, QColor(d.palette[i].hex));
    for (int i = 0; i < d.disabledCount; ++i) pal.setColor(QPalette::Disabled, d.disabled[i].role, QColor(d.disabled[i].hex));
    return pal;
}

inline QString stylesheet(Variant v) { return QString::fromUtf8(detail::data(v).qss); }

/// Theme the whole application.
inline void apply(QApplication& app, Variant v = Variant::Round, const QString& fontsDir = {}) {
    const auto& d = detail::data(v);
    loadFonts(fontsDir);
    QDir::setSearchPaths("mono", {detail::iconDir(d)});
    app.setStyle(QStyleFactory::create("Fusion"));
    app.setPalette(palette(v));
    QFont f(QString::fromUtf8(d.fontSans));
    f.setPixelSize(d.uiPx);
    app.setFont(f);
    app.setStyleSheet(stylesheet(v));
    app.setProperty("monoVariant", QString::fromUtf8(d.name));
}

/// Mark a widget with a stylesheet role: h1, h2, h3, label, muted, faint, mono, stat (labels); card, panel, rule, stats, cell (frames).
inline QWidget* setRole(QWidget* w, const char* role) {
    w->setProperty("role", role);
    if (qstrcmp(role, "label") == 0) {
        const auto& d = detail::data(qApp ? qApp->property("monoVariant").toString() : QString("round"));
        QFont f = w->font();
        if (d.labelUpper) f.setCapitalization(QFont::AllUppercase);
        f.setLetterSpacing(QFont::PercentageSpacing, 100 + d.labelTracking * 100);
        w->setFont(f);
    }
    w->style()->unpolish(w);
    w->style()->polish(w);
    return w;
}

/// Button style: "fill", "line" or "ghost" (default is outline).
inline QWidget* setKind(QWidget* w, const char* kind) {
    w->setProperty("kind", kind);
    w->style()->unpolish(w);
    w->style()->polish(w);
    return w;
}

}  // namespace monoui
""")
    p = o / "cpp" / "mono_qt.hpp"
    write(p, "\n".join(parts))
    return p
