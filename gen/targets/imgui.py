"""Dear ImGui: header-only C++ style + font loader.

    #include "mono_imgui.h"
    MonoUI::ApplyStyle(MonoUI::Round);
    MonoUI::LoadFonts("mono-ui/fonts/ttf", 16.0f);   // optional
"""
from __future__ import annotations

from pathlib import Path

from tokens import HEADER, Tokens, fmt, write

# ImGuiCol_* -> token role (solid colours, alpha where it helps)
COLS = [
    ("Text", "fg"), ("TextDisabled", "disabled"), ("WindowBg", "bg"), ("ChildBg", "bg"), ("PopupBg", "surface"),
    ("Border", "line"), ("BorderShadow", None), ("FrameBg", "bgAlt"), ("FrameBgHovered", "surface"),
    ("FrameBgActive", "surfaceAlt"), ("TitleBg", "bgAlt"), ("TitleBgActive", "surface"), ("TitleBgCollapsed", "bgAlt"),
    ("MenuBarBg", "bgAlt"), ("ScrollbarBg", None), ("ScrollbarGrab", "lineStrong"), ("ScrollbarGrabHovered", "fgMuted"),
    ("ScrollbarGrabActive", "fg"), ("CheckMark", "onAccent"), ("SliderGrab", "fg"), ("SliderGrabActive", "fgStrong"),
    ("Button", None), ("ButtonHovered", "tint"), ("ButtonActive", "surfaceAlt"), ("Header", "selection"),
    ("HeaderHovered", "surfaceAlt"), ("HeaderActive", "selection"), ("Separator", "line"), ("SeparatorHovered", "lineStrong"),
    ("SeparatorActive", "fg"), ("ResizeGrip", "line"), ("ResizeGripHovered", "lineStrong"), ("ResizeGripActive", "fg"),
    ("InputTextCursor", "fgStrong"), ("TabHovered", "surfaceAlt"), ("Tab", None), ("TabSelected", "surface"),
    ("TabSelectedOverline", "fg"), ("TabDimmed", None), ("TabDimmedSelected", "surface"), ("TabDimmedSelectedOverline", "lineStrong"),
    ("PlotLines", "fgDim"), ("PlotLinesHovered", "fgStrong"), ("PlotHistogram", "fgDim"), ("PlotHistogramHovered", "fgStrong"),
    ("TableHeaderBg", "bgAlt"), ("TableBorderStrong", "line"), ("TableBorderLight", "lineSoft"), ("TableRowBg", None),
    ("TableRowBgAlt", "tint"), ("TextLink", "fgStrong"), ("TextSelectedBg", "selection"), ("TreeLines", "line"),
    ("DragDropTarget", "fgStrong"), ("DragDropTargetBg", "tint"), ("UnsavedMarker", "fgStrong"), ("CheckboxSelectedBg", "accent"), ("NavCursor", "focus"), ("NavWindowingHighlight", "fgStrong"),
    ("NavWindowingDimBg", "shadow"), ("ModalWindowDimBg", "shadow"),
]


def flt(x: float) -> str:
    s = fmt(x)
    return (s if "." in s else s + ".0") + "f"


def vec4(c) -> str:
    r, g, b, a = c.floats()
    return f"ImVec4({flt(r)}, {flt(g)}, {flt(b)}, {flt(a)})"


def build(t: Tokens, out: Path) -> list[Path]:
    o = out / "imgui"
    parts = [f"""// mono-ui for Dear ImGui (1.91+). {HEADER}
//
//   #include "imgui.h"
//   #include "mono_imgui.h"
//   MonoUI::ApplyStyle(MonoUI::Round);                 // or Square, Blend, Paper
//   MonoUI::LoadFonts("path/to/mono-ui/fonts/ttf");    // optional, call before the first frame
//
//   Buttons: MonoUI::ButtonFill("Save"), MonoUI::ButtonLine("Cancel"), MonoUI::ButtonGhost("More")
//   Text:    MonoUI::Label("SECTION"), MonoUI::Muted("..."), MonoUI::Heading("Title")
#pragma once

#include "imgui.h"
#include <cstdio>
#include <string>

namespace MonoUI {{

enum Variant {{ {', '.join(f'{v.capitalize()} = {i}' for i, v in enumerate(t.variants))} }};

struct Palette {{
    ImVec4 bg, bgAlt, surface, surfaceAlt, fgStrong, fg, fgDim, fgMuted, fgFaint;
    ImVec4 lineSoft, line, lineStrong, focus, tint, accent, accentHover, onAccent, selection, onSelection, disabled, shadow;
}};

struct Fonts {{
    ImFont* sans = nullptr; ImFont* strong = nullptr; ImFont* mono = nullptr; ImFont* display = nullptr;
    float sansPx = 0, monoPx = 0, displayPx = 0;
}};

// ImGui 1.92 made font sizes dynamic and PushFont() takes a size; older versions bake the size in.
inline void PushFontSized(ImFont* font, float px) {{
#if IMGUI_VERSION_NUM >= 19200
    ImGui::PushFont(font, px);
#else
    (void)px;
    ImGui::PushFont(font);
#endif
}}
"""]
    roles_order = ["bg", "bgAlt", "surface", "surfaceAlt", "fgStrong", "fg", "fgDim", "fgMuted", "fgFaint", "lineSoft",
                   "line", "lineStrong", "focus", "tint", "accent", "accentHover", "onAccent", "selection", "onSelection",
                   "disabled", "shadow"]
    for v in t.variants:
        roles = t.roles(v)
        # ImGui blends alpha itself, so translucent roles stay translucent
        parts.append(f"inline const Palette& Palette{v.capitalize()}() {{")
        parts.append("    static const Palette p = {")
        parts.append("        " + ",\n        ".join(vec4(roles[r]) for r in roles_order))
        parts.append("    };")
        parts.append("    return p;")
        parts.append("}")
    parts.append("""
inline Variant& CurrentVariant() { static Variant v = Round; return v; }
inline const Palette& Colors() {
    switch (CurrentVariant()) {
""" + "".join(f"        case {v.capitalize()}: return Palette{v.capitalize()}();\n" for v in t.variants) + """    }
    return PaletteRound();
}
inline Fonts& LoadedFonts() { static Fonts f; return f; }

inline void ApplyStyle(Variant v = Round, ImGuiStyle* dst = nullptr) {
    CurrentVariant() = v;
    ImGuiStyle& s = dst ? *dst : ImGui::GetStyle();
    const Palette& p = Colors();
    const ImVec4 none(0, 0, 0, 0);
    ImVec4* c = s.Colors;""")
    # colours that only exist in newer ImGui versions -> IMGUI_VERSION_NUM they arrived in
    newer = {"InputTextCursor": 19200, "TreeLines": 19200, "UnsavedMarker": 19240, "DragDropTargetBg": 19250,
             "CheckboxSelectedBg": 19280}
    for col, role in COLS:
        val = "none" if role is None else f"p.{role}"
        line = f"    c[ImGuiCol_{col}] = {val};"
        parts.append(f"#if IMGUI_VERSION_NUM >= {newer[col]}\n{line}\n#endif" if col in newer else line)
    parts.append("    c[ImGuiCol_CheckMark] = p.onAccent;  // drawn on an accent-filled box, see Checkbox() below")
    # geometry per variant
    geo = {}
    for v in t.variants:
        d = t.v(v)
        r = d["radius"]
        geo[v] = dict(window=r["lg"], child=r["md"], popup=r["md"], frame=r["md"], grab=(7 if r["md"] else 0),
                      tab=r["md"], scroll=(4 if r["md"] else 0), padx=d["control"]["padX"],
                      pady=(6 if r["md"] == 0 else 4))
    arr = lambda key: "{" + ", ".join(f"{geo[v][key]}.0f" for v in t.variants) + "}"
    parts.append("    const int i = (int)v;")
    for field, key in (("WindowRounding", "window"), ("ChildRounding", "child"), ("PopupRounding", "popup"),
                       ("FrameRounding", "frame"), ("GrabRounding", "grab"), ("TabRounding", "tab"),
                       ("ScrollbarRounding", "scroll")):
        parts.append(f"    {{ static const float k[] = {arr(key)}; s.{field} = k[i]; }}")
    parts.append(f"    {{ static const float x[] = {arr('padx')}, y[] = {arr('pady')}; s.FramePadding = ImVec2(x[i], y[i]); }}")
    parts.append("""    s.WindowBorderSize = 1.0f;
    s.ChildBorderSize = 1.0f;
    s.PopupBorderSize = 1.0f;
    s.FrameBorderSize = 1.0f;
    s.TabBorderSize = 1.0f;
    s.TabBarBorderSize = 1.0f;
    s.WindowPadding = ImVec2(16.0f, 14.0f);
    s.ItemSpacing = ImVec2(10.0f, 8.0f);
    s.ItemInnerSpacing = ImVec2(8.0f, 6.0f);
    s.CellPadding = ImVec2(8.0f, 6.0f);
    s.IndentSpacing = 18.0f;
    s.ScrollbarSize = 10.0f;
    s.GrabMinSize = 12.0f;
    s.WindowTitleAlign = ImVec2(0.0f, 0.5f);
    s.SeparatorTextBorderSize = 1.0f;
    s.SeparatorTextPadding = ImVec2(0.0f, 4.0f);
    s.WindowMenuButtonPosition = ImGuiDir_None;
    s.AntiAliasedLines = true;
    s.AntiAliasedFill = true;
}

// ---------- fonts ----------

namespace detail {
inline bool exists(const std::string& p) { FILE* f = std::fopen(p.c_str(), "rb"); if (f) std::fclose(f); return f != nullptr; }
inline ImFont* add(const std::string& dir, const char* file, float px) {
    const std::string path = dir + "/" + file;
    if (!exists(path)) return nullptr;
    ImFontConfig cfg; cfg.OversampleH = 2; cfg.OversampleV = 1;
    return ImGui::GetIO().Fonts->AddFontFromFileTTF(path.c_str(), px, &cfg);
}
}  // namespace detail

/// Load the variant's fonts from mono-ui/fonts/ttf. The sans font becomes the default.
inline Fonts& LoadFonts(const char* ttfDir, float px = 0.0f) {
    Fonts& f = LoadedFonts();
    const std::string dir(ttfDir ? ttfDir : "");
    const int i = (int)CurrentVariant();""")
    q = lambda xs: "{" + ", ".join(xs) + "}"
    parts.append(f"    static const float basePx[] = {q(f'{t.app_px(v)}.0f' for v in t.variants)};")
    parts.append(f"    static const float scale[] = {q(flt(t.display_scale(v)) for v in t.variants)};")
    for role in ("sans", "strong", "mono", "display"):
        parts.append(f"    static const char* {role}File[] = {q(chr(34) + t.font_files(v)[role] + chr(34) for v in t.variants)};")
    parts.append("""    if (px <= 0.0f) px = basePx[i];
    f.sansPx = px;
    f.monoPx = px;
    f.displayPx = px * scale[i];
    f.sans = detail::add(dir, sansFile[i], px);
    f.strong = std::string(strongFile[i]) == sansFile[i] ? f.sans : detail::add(dir, strongFile[i], px);
    f.mono = detail::add(dir, monoFile[i], px * (std::string(monoFile[i]).rfind("Space", 0) == 0 ? 0.9f : 1.0f));
    f.display = detail::add(dir, displayFile[i], f.displayPx);
    if (f.sans) ImGui::GetIO().FontDefault = f.sans;
    return f;
}

// ---------- widgets in the mono style ----------

inline bool LabelUppercase() {
    static const bool up[] = """ + "{" + ", ".join(str(t.v(v)["label"]["uppercase"]).lower() for v in t.variants) + "}" + """;
    return up[(int)CurrentVariant()];
}

inline void Label(const char* text) {
    const bool sq = LabelUppercase();
    if (LoadedFonts().strong) PushFontSized(LoadedFonts().strong, LoadedFonts().sansPx);
    ImGui::PushStyleColor(ImGuiCol_Text, Colors().fgMuted);
    if (sq) {
        std::string up(text);
        for (auto& ch : up) ch = (char)toupper((unsigned char)ch);
        ImGui::TextUnformatted(up.c_str());
    } else {
        ImGui::TextUnformatted(text);
    }
    ImGui::PopStyleColor();
    if (LoadedFonts().strong) ImGui::PopFont();
}

inline void Heading(const char* text) {
    if (LoadedFonts().display) PushFontSized(LoadedFonts().display, LoadedFonts().displayPx);
    ImGui::PushStyleColor(ImGuiCol_Text, Colors().fg);
    ImGui::TextUnformatted(text);
    ImGui::PopStyleColor();
    if (LoadedFonts().display) ImGui::PopFont();
}

inline void Muted(const char* text) { ImGui::PushStyleColor(ImGuiCol_Text, Colors().fgMuted); ImGui::TextUnformatted(text); ImGui::PopStyleColor(); }
inline void Faint(const char* text) { ImGui::PushStyleColor(ImGuiCol_Text, Colors().fgFaint); ImGui::TextUnformatted(text); ImGui::PopStyleColor(); }
inline void Mono(const char* text) {
    if (LoadedFonts().mono) PushFontSized(LoadedFonts().mono, LoadedFonts().monoPx);
    ImGui::PushStyleColor(ImGuiCol_Text, Colors().fgDim); ImGui::TextUnformatted(text); ImGui::PopStyleColor();
    if (LoadedFonts().mono) ImGui::PopFont();
}

/// Filled (accent) button.
inline bool ButtonFill(const char* label, const ImVec2& size = ImVec2(0, 0)) {
    const Palette& p = Colors();
    ImGui::PushStyleColor(ImGuiCol_Button, p.accent);
    ImGui::PushStyleColor(ImGuiCol_ButtonHovered, p.accentHover);
    ImGui::PushStyleColor(ImGuiCol_ButtonActive, p.fgMuted);
    ImGui::PushStyleColor(ImGuiCol_Text, p.onAccent);
    ImGui::PushStyleColor(ImGuiCol_Border, p.accent);
    const bool r = ImGui::Button(label, size);
    ImGui::PopStyleColor(5);
    return r;
}

/// Outline button with the strong line colour.
inline bool ButtonLine(const char* label, const ImVec2& size = ImVec2(0, 0)) {
    ImGui::PushStyleColor(ImGuiCol_Border, Colors().lineStrong);
    const bool r = ImGui::Button(label, size);
    ImGui::PopStyleColor();
    return r;
}

/// Borderless, muted button.
inline bool ButtonGhost(const char* label, const ImVec2& size = ImVec2(0, 0)) {
    ImGui::PushStyleColor(ImGuiCol_Border, ImVec4(0, 0, 0, 0));
    ImGui::PushStyleColor(ImGuiCol_Text, Colors().fgMuted);
    const bool r = ImGui::Button(label, size);
    ImGui::PopStyleColor(2);
    return r;
}

/// Checkbox whose box fills with the accent colour when ticked (like the web/Qt versions).
inline bool Checkbox(const char* label, bool* v) {
#if IMGUI_VERSION_NUM >= 19280
    return ImGui::Checkbox(label, v);  // ImGuiCol_CheckboxSelectedBg already does this
#endif
    const Palette& p = Colors();
    if (*v) {
        ImGui::PushStyleColor(ImGuiCol_FrameBg, p.accent);
        ImGui::PushStyleColor(ImGuiCol_FrameBgHovered, p.accentHover);
        ImGui::PushStyleColor(ImGuiCol_FrameBgActive, p.accentHover);
    }
    const bool was = *v;
    const bool r = ImGui::Checkbox(label, v);
    if (was) ImGui::PopStyleColor(3);
    return r;
}

/// A row of big numbers with labels underneath, in a bordered strip.
inline void Stats(const char* const* numbers, const char* const* labels, int count) {
    const Palette& p = Colors();
    ImDrawList* dl = ImGui::GetWindowDrawList();
    const ImVec2 start = ImGui::GetCursorScreenPos();
    const float w = ImGui::GetContentRegionAvail().x;
    const float cellW = w / (float)count;
    ImFont* big = LoadedFonts().display;
    const float bigSize = big ? LoadedFonts().displayPx * 0.85f : ImGui::GetFontSize() * 1.8f;
    const float h = bigSize + ImGui::GetFontSize() + 26.0f;
    const float rounding = ImGui::GetStyle().FrameRounding;
    dl->AddRect(start, ImVec2(start.x + w, start.y + h), ImGui::GetColorU32(p.line), rounding);
    for (int i = 0; i < count; ++i) {
        const float x = start.x + cellW * (float)i;
        if (i) dl->AddLine(ImVec2(x, start.y), ImVec2(x, start.y + h), ImGui::GetColorU32(p.line));
        dl->AddText(big ? big : ImGui::GetFont(), bigSize, ImVec2(x + 14.0f, start.y + 10.0f), ImGui::GetColorU32(p.fg), numbers[i]);
        dl->AddText(ImVec2(x + 14.0f, start.y + 14.0f + bigSize), ImGui::GetColorU32(p.fgMuted), labels[i]);
    }
    ImGui::Dummy(ImVec2(w, h));
}

}  // namespace MonoUI
""")
    p = o / "mono_imgui.h"
    write(p, "\n".join(parts))
    return [p]
