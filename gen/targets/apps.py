"""More app toolkits: Tkinter, Dear PyGui, Java Swing, Rust egui, Rust iced, Go Fyne, C# Avalonia.

Each one gets both variants as data plus an apply()/theme function in that language.
"""
from __future__ import annotations

import json
from pathlib import Path

from tokens import HEADER, Tokens, write

ROLES = ["bg", "bgAlt", "surface", "surfaceAlt", "fgStrong", "fg", "fgDim", "fgMuted", "fgFaint", "lineSoft",
         "line", "lineStrong", "focus", "tint", "accent", "accentHover", "onAccent", "selection", "onSelection",
         "disabled", "shadow"]
def snake(s: str) -> str:
    return "".join("_" + c.lower() if c.isupper() else c for c in s)


def variant_data(t: Tokens, v: str) -> dict:
    d = t.v(v)
    return {
        "color": {k: c.hex for k, c in t.solid(v).items()},
        "font": {k: f["family"] for k, f in d["font"].items()},
        "fontFile": t.font_files(v),
        "weight": {k: f["weight"] for k, f in d["font"].items()},
        "size": d["size"], "radius": d["radius"], "border": d["border"], "control": d["control"],
        "label": d["label"], "light": t.light(v), "appPx": t.app_px(v), "displayScale": t.display_scale(v),
    }


def build(t: Tokens, out: Path) -> list[Path]:
    o = out / "apps"
    data = {v: variant_data(t, v) for v in t.variants}
    return [tkinter(o, data), dearpygui(o, data), swing(o, data), egui(o, data), iced(o, data),
            fyne(o, data), *avalonia(o, data)]


# ---------------------------------------------------------------- Tkinter

def tkinter(o: Path, data: dict) -> Path:
    text = f'''"""mono-ui for Tkinter (ttk). {HEADER}

    import tkinter as tk
    from mono_tk import apply
    root = tk.Tk()
    style = apply(root, "round")            # or "square", "blend", "paper"
    ttk.Button(root, text="Save", style="Fill.TButton")
    ttk.Label(root, text="Title", style="H1.TLabel")

Styles: H1/H2/H3/Label/Muted/Faint/Mono.TLabel, Fill/Line/Ghost.TButton, Card.TFrame, Card.TLabel.
Tk can't round corners, so every variant is square here; they differ in greys and type.
Fonts: apply() registers mono-ui/fonts/ttf with fontconfig if the families aren't installed.
"""
from __future__ import annotations

import ctypes
import ctypes.util
import json
import os
from pathlib import Path
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

_DATA = json.loads(r"""{json.dumps(data)}""")


def _font_dir():
    env = os.environ.get("MONO_UI_FONTS")
    if env:
        return Path(env)
    for up in Path(__file__).resolve().parents:
        if (up / "fonts" / "ttf").is_dir():
            return up / "fonts" / "ttf"
    return None


def load_fonts() -> int:
    """Register the bundled TTFs with fontconfig (Linux). Must run before Tk() for Tk to see them."""
    d = _font_dir()
    lib = ctypes.util.find_library("fontconfig")
    if not d or not lib:
        return 0
    fc = ctypes.CDLL(lib)
    fc.FcConfigGetCurrent.restype = ctypes.c_void_p
    fc.FcConfigAppFontAddFile.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
    cfg = fc.FcConfigGetCurrent()
    return sum(bool(fc.FcConfigAppFontAddFile(cfg, str(f).encode())) for f in d.glob("*.ttf"))


load_fonts()  # at import, so it happens before the caller creates Tk()


def colors(variant: str = "round") -> dict:
    return _DATA[variant]["color"]


def apply(root: tk.Misc, variant: str = "round") -> ttk.Style:
    d = _DATA[variant]
    c, f, s = d["color"], d["font"], d["size"]
    label_upper = d["label"]["uppercase"]
    fam = lambda k: f[k] if f[k] in tkfont.families(root) else "TkDefaultFont"
    sans, strong, mono, display = fam("sans"), fam("strong"), fam("mono"), fam("display")
    bold = "bold" if d["weight"]["strong"] >= 500 else "normal"

    root.configure(background=c["bg"])
    root._mono_variant = variant
    # named fonts, not option_add("*Font"): the option database would override ttk style fonts
    for name in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont"):
        try:
            tkfont.nametofont(name, root).configure(family=sans, size=-s["ui"])
        except tk.TclError:
            pass
    tkfont.nametofont("TkFixedFont", root).configure(family=mono, size=-s["small"])
    root.option_add("*TCombobox*Listbox.background", c["surface"])
    root.option_add("*TCombobox*Listbox.foreground", c["fg"])
    root.option_add("*TCombobox*Listbox.selectBackground", c["selection"])
    root.option_add("*TCombobox*Listbox.selectForeground", c["onSelection"])
    for opt, val in (("background", c["surface"]), ("foreground", c["fg"]), ("activeBackground", c["selection"]),
                     ("activeForeground", c["onSelection"]), ("relief", "flat")):
        root.option_add(f"*Menu.{{opt}}", val)

    st = ttk.Style(root)
    st.theme_use("clam")
    base = dict(background=c["bg"], foreground=c["fgDim"], fieldbackground=c["bgAlt"], bordercolor=c["line"],
                lightcolor=c["bg"], darkcolor=c["bg"], troughcolor=c["lineSoft"], focuscolor=c["focus"],
                selectbackground=c["selection"], selectforeground=c["onSelection"], insertcolor=c["fgStrong"],
                font=(sans, -s["ui"]))
    st.configure(".", **base)
    st.map(".", foreground=[("disabled", c["disabled"])])

    # labels
    st.configure("TLabel", background=c["bg"], foreground=c["fgDim"])
    st.configure("H1.TLabel", foreground=c["fg"], font=(display, -min(s["h2"], 48)))
    st.configure("H2.TLabel", foreground=c["fg"], font=(display, -round((min(s["h2"], 48) + s["h3"]) / 2)))
    st.configure("H3.TLabel", foreground=c["fg"], font=(strong, -s["h3"], bold))
    st.configure("Label.TLabel", foreground=c["fgMuted"], font=(strong, -s["label"], bold))
    st.configure("Muted.TLabel", foreground=c["fgMuted"])
    st.configure("Faint.TLabel", foreground=c["fgFaint"])
    st.configure("Mono.TLabel", foreground=c["fgDim"], font=(mono, -s["small"]))
    st.configure("Stat.TLabel", foreground=c["fg"], font=(display, -s["stat"]))
    st._mono_upper = label_upper  # for label() below

    # frames
    st.configure("TFrame", background=c["bg"])
    st.configure("Card.TFrame", background=c["surface"], bordercolor=c["line"], relief="solid", borderwidth=1)
    st.configure("Card.TLabel", background=c["surface"], foreground=c["fgDim"])
    st.configure("TLabelframe", background=c["bg"], bordercolor=c["line"], relief="solid")
    st.configure("TLabelframe.Label", background=c["bg"], foreground=c["fgMuted"], font=(strong, -s["label"], bold))
    st.configure("TSeparator", background=c["line"])

    # buttons
    pad = (d["control"]["padX"], max(2, (d["control"]["height"] - s["ui"] - 8) // 2))
    btn = dict(background=c["bg"], foreground=c["fg"], bordercolor=c["fg"], lightcolor=c["bg"], darkcolor=c["bg"],
               relief="solid", borderwidth=1, padding=pad, font=(strong, -s["label"], bold), focusthickness=0)
    st.configure("TButton", **btn)
    st.map("TButton", background=[("pressed", c["surfaceAlt"]), ("active", c["surface"])],
           bordercolor=[("disabled", c["line"])], foreground=[("disabled", c["disabled"])])
    st.configure("Fill.TButton", **{{**btn, "background": c["accent"], "foreground": c["onAccent"], "bordercolor": c["accent"],
                                    "lightcolor": c["accent"], "darkcolor": c["accent"]}})
    st.map("Fill.TButton", background=[("active", c["accentHover"])], lightcolor=[("active", c["accentHover"])],
           darkcolor=[("active", c["accentHover"])], bordercolor=[("active", c["accentHover"])])
    st.configure("Line.TButton", **{{**btn, "bordercolor": c["lineStrong"]}})
    st.map("Line.TButton", bordercolor=[("active", c["fg"])], background=[("active", c["surface"])])
    st.configure("Ghost.TButton", **{{**btn, "bordercolor": c["bg"], "foreground": c["fgMuted"]}})
    st.map("Ghost.TButton", foreground=[("active", c["fg"])], background=[("active", c["surface"])],
           bordercolor=[("active", c["surface"])])

    # inputs
    field = dict(fieldbackground=c["bgAlt"], foreground=c["fg"], bordercolor=c["line"], lightcolor=c["bgAlt"],
                 darkcolor=c["bgAlt"], padding=(8, 4), insertcolor=c["fgStrong"])
    for w in ("TEntry", "TSpinbox", "TCombobox"):
        st.configure(w, **field)
        st.map(w, bordercolor=[("focus", c["focus"]), ("hover", c["lineStrong"])],
               lightcolor=[("focus", c["bgAlt"])], fieldbackground=[("readonly", c["bgAlt"])],
               foreground=[("disabled", c["disabled"])])
    st.configure("TCombobox", arrowcolor=c["fgMuted"], background=c["bgAlt"])
    st.configure("TSpinbox", arrowcolor=c["fgMuted"], background=c["bgAlt"])
    for w in ("TCheckbutton", "TRadiobutton"):
        st.configure(w, background=c["bg"], foreground=c["fg"], indicatorbackground=c["bgAlt"],
                     indicatorforeground=c["onAccent"], indicatormargin=(0, 0, 8, 0), upperbordercolor=c["lineStrong"],
                     lowerbordercolor=c["lineStrong"])
        st.map(w, indicatorbackground=[("selected", c["accent"])], background=[("active", c["bg"])])
    st.configure("Horizontal.TScale", background=c["fgStrong"], troughcolor=c["lineStrong"], bordercolor=c["bg"],
                 lightcolor=c["fgStrong"], darkcolor=c["fgStrong"], sliderthickness=14)
    st.configure("Horizontal.TProgressbar", background=c["fg"], troughcolor=c["lineSoft"], bordercolor=c["bg"],
                 lightcolor=c["fg"], darkcolor=c["fg"], thickness=4)

    # tabs, trees, scrollbars
    st.configure("TNotebook", background=c["bg"], bordercolor=c["line"], tabmargins=(0, 0, 0, 0))
    st.configure("TNotebook.Tab", background=c["bg"], foreground=c["fgMuted"], bordercolor=c["bg"],
                 lightcolor=c["bg"], padding=(14, 6), font=(strong, -s["label"], bold))
    st.map("TNotebook.Tab", background=[("selected", c["bg"])], foreground=[("selected", c["fg"])],
           bordercolor=[("selected", c["line"])], lightcolor=[("selected", c["bg"])])
    st.configure("Treeview", background=c["bgAlt"], fieldbackground=c["bgAlt"], foreground=c["fg"],
                 bordercolor=c["line"], rowheight=s["ui"] + 14)
    st.map("Treeview", background=[("selected", c["selection"])], foreground=[("selected", c["onSelection"])])
    st.configure("Treeview.Heading", background=c["bgAlt"], foreground=c["fgMuted"], bordercolor=c["line"],
                 relief="flat", font=(strong, -s["label"], bold), padding=(8, 6))
    st.map("Treeview.Heading", background=[("active", c["surface"])])
    for orient in ("Vertical", "Horizontal"):
        st.configure(f"{{orient}}.TScrollbar", background=c["lineStrong"], troughcolor=c["bg"], bordercolor=c["bg"],
                     lightcolor=c["lineStrong"], darkcolor=c["lineStrong"], arrowcolor=c["fgMuted"], arrowsize=10)
    return st


def label(parent, text: str, role: str = "Label", variant: str | None = None, **kw) -> ttk.Label:
    """A ttk.Label in one of the mono roles. "Label" is uppercased in variants that want it."""
    v = variant or getattr(parent._root(), "_mono_variant", "round")
    if role == "Label" and _DATA[v]["label"]["uppercase"]:
        text = text.upper()
    return ttk.Label(parent, text=text, style=f"{{role}}.TLabel", **kw)
'''
    p = o / "tkinter" / "mono_tk.py"
    write(p, text)
    return p


# ---------------------------------------------------------------- Dear PyGui

def dearpygui(o: Path, data: dict) -> Path:
    text = f'''"""mono-ui for Dear PyGui. {HEADER}

    import dearpygui.dearpygui as dpg
    import mono_dpg
    dpg.create_context()
    themes = mono_dpg.apply("round")       # or "square", "blend", "paper"; binds the theme, loads fonts
    dpg.add_button(label="Save"); dpg.bind_item_theme(dpg.last_item(), themes["fill"])
    dpg.add_text("Title"); dpg.bind_item_font(dpg.last_item(), themes["fonts"]["display"])
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import dearpygui.dearpygui as dpg

_DATA = json.loads(r"""{json.dumps(data)}""")


def _rgba(hexv: str, a: int = 255):
    h = hexv.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def _font_dir():
    env = os.environ.get("MONO_UI_FONTS")
    if env:
        return Path(env)
    for up in Path(__file__).resolve().parents:
        if (up / "fonts" / "ttf").is_dir():
            return up / "fonts" / "ttf"
    return None


def apply(variant: str = "round", font_px: int | None = None) -> dict:
    """Create and bind the mono theme. Returns {{"global", "fill", "line", "ghost", "muted", "fonts": {{...}}}}."""
    d = _DATA[variant]
    c, r = d["color"], d["radius"]
    C = lambda k, a=255: _rgba(c[k], a)
    out = {{}}
    with dpg.theme() as g:
        with dpg.theme_component(dpg.mvAll):
            for col, val in [
                (dpg.mvThemeCol_Text, C("fg")), (dpg.mvThemeCol_TextDisabled, C("disabled")),
                (dpg.mvThemeCol_WindowBg, C("bg")), (dpg.mvThemeCol_ChildBg, C("bg")), (dpg.mvThemeCol_PopupBg, C("surface")),
                (dpg.mvThemeCol_Border, C("line")), (dpg.mvThemeCol_BorderShadow, (0, 0, 0, 0)),
                (dpg.mvThemeCol_FrameBg, C("bgAlt")), (dpg.mvThemeCol_FrameBgHovered, C("surface")),
                (dpg.mvThemeCol_FrameBgActive, C("surfaceAlt")), (dpg.mvThemeCol_TitleBg, C("bgAlt")),
                (dpg.mvThemeCol_TitleBgActive, C("surface")), (dpg.mvThemeCol_MenuBarBg, C("bgAlt")),
                (dpg.mvThemeCol_ScrollbarBg, (0, 0, 0, 0)), (dpg.mvThemeCol_ScrollbarGrab, C("lineStrong")),
                (dpg.mvThemeCol_ScrollbarGrabHovered, C("fgMuted")), (dpg.mvThemeCol_ScrollbarGrabActive, C("fg")),
                (dpg.mvThemeCol_CheckMark, C("fgStrong")), (dpg.mvThemeCol_SliderGrab, C("fg")),
                (dpg.mvThemeCol_SliderGrabActive, C("fgStrong")), (dpg.mvThemeCol_Button, (0, 0, 0, 0)),
                (dpg.mvThemeCol_ButtonHovered, C("surface")), (dpg.mvThemeCol_ButtonActive, C("surfaceAlt")),
                (dpg.mvThemeCol_Header, C("selection")), (dpg.mvThemeCol_HeaderHovered, C("surfaceAlt")),
                (dpg.mvThemeCol_HeaderActive, C("selection")), (dpg.mvThemeCol_Separator, C("line")),
                (dpg.mvThemeCol_Tab, (0, 0, 0, 0)), (dpg.mvThemeCol_TabHovered, C("surfaceAlt")),
                (dpg.mvThemeCol_TabActive, C("surface")), (dpg.mvThemeCol_PlotLines, C("fgDim")),
                (dpg.mvThemeCol_PlotHistogram, C("fgDim")), (dpg.mvThemeCol_TableHeaderBg, C("bgAlt")),
                (dpg.mvThemeCol_TableBorderStrong, C("line")), (dpg.mvThemeCol_TableBorderLight, C("lineSoft")),
                (dpg.mvThemeCol_TableRowBgAlt, C("surface", 90)), (dpg.mvThemeCol_TextSelectedBg, C("selection")),
                (dpg.mvThemeCol_ModalWindowDimBg, (0, 0, 0, 110)),
            ]:
                dpg.add_theme_color(col, val, category=dpg.mvThemeCat_Core)
            sq = r["md"] == 0  # square corners
            for var, val in [
                (dpg.mvStyleVar_WindowRounding, r["lg"]), (dpg.mvStyleVar_ChildRounding, r["md"]),
                (dpg.mvStyleVar_FrameRounding, r["md"]), (dpg.mvStyleVar_PopupRounding, r["md"]),
                (dpg.mvStyleVar_GrabRounding, 0 if sq else 7), (dpg.mvStyleVar_TabRounding, r["md"]),
                (dpg.mvStyleVar_ScrollbarRounding, 0 if sq else 4), (dpg.mvStyleVar_FrameBorderSize, 1),
                (dpg.mvStyleVar_WindowBorderSize, 1), (dpg.mvStyleVar_ChildBorderSize, 1), (dpg.mvStyleVar_PopupBorderSize, 1),
                (dpg.mvStyleVar_ScrollbarSize, 10), (dpg.mvStyleVar_GrabMinSize, 12),
            ]:
                dpg.add_theme_style(var, val, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, d["control"]["padX"], 6 if sq else 4, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 10, 8, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 16, 14, category=dpg.mvThemeCat_Core)
    out["global"] = g

    def button_theme(**cols):
        with dpg.theme() as th:
            with dpg.theme_component(dpg.mvButton):
                for k, val in cols.items():
                    dpg.add_theme_color(getattr(dpg, f"mvThemeCol_{{k}}"), val, category=dpg.mvThemeCat_Core)
        return th

    out["fill"] = button_theme(Button=C("accent"), ButtonHovered=C("accentHover"), ButtonActive=C("fgMuted"),
                               Text=C("onAccent"), Border=C("accent"))
    out["line"] = button_theme(Border=C("lineStrong"))
    out["ghost"] = button_theme(Border=(0, 0, 0, 0), Text=C("fgMuted"))
    with dpg.theme() as muted:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, C("fgMuted"), category=dpg.mvThemeCat_Core)
    out["muted"] = muted
    with dpg.theme() as faint:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Text, C("fgFaint"), category=dpg.mvThemeCat_Core)
    out["faint"] = faint

    fonts = {{}}
    fd = _font_dir()
    px = font_px or d["appPx"]
    if fd:
        with dpg.font_registry():
            for role, scale in (("sans", 1.0), ("strong", 1.0), ("mono", 1.0), ("display", d["displayScale"])):
                path = fd / d["fontFile"][role]
                if path.exists():
                    fonts[role] = dpg.add_font(str(path), round(px * scale))
        if "sans" in fonts:
            dpg.bind_font(fonts["sans"])
    out["fonts"] = fonts
    dpg.bind_theme(g)
    return out
'''
    p = o / "dearpygui" / "mono_dpg.py"
    write(p, text)
    return p


# ---------------------------------------------------------------- Swing

def java_color(hexv: str) -> str:
    return f"new Color(0x{hexv[1:]})"


def swing(o: Path, data: dict) -> Path:
    VS = list(data)
    ints = lambda f: "new int[]{" + ", ".join(str(f(v)) for v in VS) + "}[i()]"
    strs = lambda f: "new String[]{" + ", ".join(f'"{f(v)}"' for v in VS) + "}[i()]"
    def palette(v):
        c = data[v]["color"]
        return ", ".join(f"{java_color(c[k])}" for k in ROLES)
    fields = "\n".join(f"        public final Color {k};" for k in ROLES)
    assign = "\n".join(f"            this.{k} = c[{i}];" for i, k in enumerate(ROLES))
    text = f'''// mono-ui for Java Swing. {HEADER}
//
//   MonoUI.apply(MonoUI.Variant.ROUND, Path.of("mono-ui/fonts/ttf"));   // before creating components
//   JButton save = MonoUI.button("Save", MonoUI.Kind.FILL);
//   JLabel title = MonoUI.label("Settings", MonoUI.Role.H1);
//   JPanel card = MonoUI.card();
package monoui;

import java.awt.*;
import java.awt.geom.RoundRectangle2D;
import java.io.IOException;
import java.nio.file.*;
import javax.swing.*;
import javax.swing.border.*;
import javax.swing.plaf.ColorUIResource;
import javax.swing.plaf.FontUIResource;
import javax.swing.plaf.basic.BasicButtonUI;

public final class MonoUI {{
    private MonoUI() {{}}

    public enum Variant {{ {", ".join(v.upper() for v in VS)} }}
    public enum Kind {{ OUTLINE, FILL, LINE, GHOST }}
    public enum Role {{ H1, H2, H3, LABEL, BODY, MUTED, FAINT, MONO, STAT }}

    /** Every colour role, solid. */
    public static final class Palette {{
{fields}
        Palette(Color... c) {{
{assign}
        }}
    }}

{chr(10).join(f"    public static final Palette {v.upper()} = new Palette({palette(v)});" for v in VS)}
    private static final Palette[] PALETTES = {{ {", ".join(v.upper() for v in VS)} }};

    private static Variant variant = Variant.ROUND;
    private static int i() {{ return variant.ordinal(); }}
    public static Palette colors() {{ return PALETTES[i()]; }}
    public static Variant variant() {{ return variant; }}
    public static int radius() {{ return {ints(lambda v: data[v]["radius"]["md"])}; }}
    public static int radiusLarge() {{ return {ints(lambda v: data[v]["radius"]["lg"])}; }}
    /** Labels (and button text) are uppercase in this variant. */
    public static boolean uppercase() {{ return new boolean[]{{{", ".join(str(data[v]["label"]["uppercase"]).lower() for v in VS)}}}[i()]; }}
    public static boolean light() {{ return new boolean[]{{{", ".join(str(data[v]["light"]).lower() for v in VS)}}}[i()]; }}

    private static String family(String role) {{
        switch (role) {{
            case "display": return {strs(lambda v: data[v]["font"]["display"])};
            case "strong": return {strs(lambda v: data[v]["font"]["strong"])};
            case "mono": return {strs(lambda v: data[v]["font"]["mono"])};
            default: return {strs(lambda v: data[v]["font"]["sans"])};
        }}
    }}
    private static int px(String size) {{
        switch (size) {{
{chr(10).join(f'            case "{k}": return {ints(lambda v: data[v]["size"][k])};' for k in data[VS[0]]["size"])}
            default: return 14;
        }}
    }}

    /** Register mono-ui's TTFs so the families above resolve. Pass null to rely on installed fonts. */
    public static int loadFonts(Path dir) {{
        if (dir == null || !Files.isDirectory(dir)) return 0;
        int n = 0;
        GraphicsEnvironment ge = GraphicsEnvironment.getLocalGraphicsEnvironment();
        try (DirectoryStream<Path> ds = Files.newDirectoryStream(dir, "*.ttf")) {{
            for (Path p : ds) {{
                try {{ if (ge.registerFont(Font.createFont(Font.TRUETYPE_FONT, p.toFile()))) n++; }}
                catch (FontFormatException | IOException ignored) {{ }}
            }}
        }} catch (IOException ignored) {{ }}
        return n;
    }}

    public static Font font(String role, String size, int style) {{
        return new Font(family(role), style, px(size));
    }}

    /** Set UIManager defaults for every standard Swing component. Call before creating any. */
    public static void apply(Variant v, Path fontsDir) {{
        variant = v;
        loadFonts(fontsDir);
        try {{ UIManager.setLookAndFeel("javax.swing.plaf.metal.MetalLookAndFeel"); }} catch (Exception ignored) {{ }}
        // Metal's combo and progress bar paint their own blue bits; the Basic delegates take our colours
        UIManager.put("ComboBoxUI", "javax.swing.plaf.basic.BasicComboBoxUI");
        UIManager.put("ProgressBarUI", "javax.swing.plaf.basic.BasicProgressBarUI");
        UIManager.put("ProgressBar.cellLength", 1); UIManager.put("ProgressBar.cellSpacing", 0);
        Palette c = colors();
        FontUIResource ui = new FontUIResource(font("sans", "ui", Font.PLAIN));
        FontUIResource uiStrong = new FontUIResource(font("strong", "label", Font.BOLD));
        String[] fonts = {{"Label", "TextField", "TextArea", "PasswordField", "ComboBox", "CheckBox", "RadioButton", "List",
                "Table", "Tree", "Menu", "MenuItem", "MenuBar", "PopupMenu", "ToolTip", "Spinner", "Panel", "ScrollPane", "ToggleButton"}};
        for (String k : fonts) UIManager.put(k + ".font", ui);
        UIManager.put("Button.font", uiStrong);
        UIManager.put("TabbedPane.font", uiStrong);
        UIManager.put("TableHeader.font", uiStrong);
        put("control", c.bg); put("info", c.surfaceAlt); put("nimbusBase", c.surface);
        put("Panel.background", c.bg); put("Viewport.background", c.bgAlt); put("ScrollPane.background", c.bg);
        put("Label.foreground", c.fgDim); put("Label.disabledForeground", c.disabled);
        put("Button.background", c.bg); put("Button.foreground", c.fg); put("Button.select", c.surfaceAlt);
        put("Button.focus", c.focus); put("Button.disabledText", c.disabled);
        put("ToggleButton.background", c.bg); put("ToggleButton.foreground", c.fg); put("ToggleButton.select", c.accent);
        for (String k : new String[]{{"TextField", "PasswordField", "TextArea", "FormattedTextField", "EditorPane", "TextPane"}}) {{
            put(k + ".background", c.bgAlt); put(k + ".foreground", c.fg); put(k + ".caretForeground", c.fgStrong);
            put(k + ".selectionBackground", c.selection); put(k + ".selectionForeground", c.onSelection);
            put(k + ".inactiveForeground", c.disabled);
            UIManager.put(k + ".border", BorderFactory.createCompoundBorder(new RoundBorder(c.line, radius()), new EmptyBorder(4, 8, 4, 8)));
        }}
        put("ComboBox.background", c.bgAlt); put("ComboBox.foreground", c.fg); put("ComboBox.buttonBackground", c.bgAlt);
        put("ComboBox.buttonShadow", c.bgAlt); put("ComboBox.buttonDarkShadow", c.fgMuted);
        put("ComboBox.buttonHighlight", c.bgAlt); put("ComboBox.disabledBackground", c.bg);
        put("ComboBox.selectionBackground", c.selection); put("ComboBox.selectionForeground", c.onSelection);
        UIManager.put("ComboBox.border", new RoundBorder(c.line, radius()));
        for (String k : new String[]{{"CheckBox", "RadioButton"}}) {{
            put(k + ".background", c.bg); put(k + ".foreground", c.fg); put(k + ".focus", c.bg);
        }}
        UIManager.put("CheckBox.icon", new CheckIcon(false)); UIManager.put("RadioButton.icon", new CheckIcon(true));
        put("Slider.background", c.bg); put("Slider.foreground", c.fg); put("Slider.focus", c.bg);
        put("ProgressBar.background", c.lineSoft); put("ProgressBar.foreground", c.fg);
        UIManager.put("ProgressBar.border", BorderFactory.createEmptyBorder());
        put("TabbedPane.background", c.bg); put("TabbedPane.foreground", c.fgMuted); put("TabbedPane.selected", c.bg);
        put("TabbedPane.contentAreaColor", c.bg); put("TabbedPane.borderHightlightColor", c.line);
        put("TabbedPane.light", c.line); put("TabbedPane.highlight", c.line); put("TabbedPane.shadow", c.line);
        put("TabbedPane.darkShadow", c.line); put("TabbedPane.focus", c.bg); put("TabbedPane.selectHighlight", c.line);
        put("TabbedPane.tabAreaBackground", c.bg); put("TabbedPane.unselectedBackground", c.bg);
        UIManager.put("TabbedPane.contentBorderInsets", new Insets(1, 1, 1, 1));
        UIManager.put("TabbedPane.tabInsets", new Insets(6, 14, 6, 14));
        put("List.background", c.bgAlt); put("List.foreground", c.fg); put("List.selectionBackground", c.selection);
        put("List.selectionForeground", c.onSelection);
        put("Table.background", c.bgAlt); put("Table.foreground", c.fg); put("Table.gridColor", c.lineSoft);
        put("Table.selectionBackground", c.selection); put("Table.selectionForeground", c.onSelection);
        put("TableHeader.background", c.bgAlt); put("TableHeader.foreground", c.fgMuted);
        UIManager.put("TableHeader.cellBorder", BorderFactory.createCompoundBorder(
                BorderFactory.createMatteBorder(0, 0, 1, 0, c.line), new EmptyBorder(6, 8, 6, 8)));
        put("Tree.background", c.bgAlt); put("Tree.foreground", c.fg); put("Tree.textBackground", c.bgAlt);
        put("Tree.textForeground", c.fg); put("Tree.selectionBackground", c.selection);
        put("Tree.selectionForeground", c.onSelection);
        put("ScrollBar.background", c.bg); put("ScrollBar.thumb", c.lineStrong); put("ScrollBar.track", c.bg);
        put("ScrollBar.thumbDarkShadow", c.lineStrong); put("ScrollBar.thumbHighlight", c.lineStrong);
        put("ScrollBar.thumbShadow", c.lineStrong); UIManager.put("ScrollBar.width", 10);
        put("Separator.foreground", c.line); put("Separator.background", c.bg);
        put("MenuBar.background", c.bg); put("MenuBar.foreground", c.fgDim);
        for (String k : new String[]{{"Menu", "MenuItem", "CheckBoxMenuItem", "RadioButtonMenuItem", "PopupMenu"}}) {{
            put(k + ".background", c.surface); put(k + ".foreground", c.fg);
            put(k + ".selectionBackground", c.selection); put(k + ".selectionForeground", c.onSelection);
        }}
        UIManager.put("PopupMenu.border", new LineBorder(c.lineStrong));
        put("ToolTip.background", c.surfaceAlt); put("ToolTip.foreground", c.fg);
        UIManager.put("ToolTip.border", BorderFactory.createCompoundBorder(new LineBorder(c.lineStrong), new EmptyBorder(4, 8, 4, 8)));
        put("OptionPane.background", c.surface); put("OptionPane.messageForeground", c.fg);
        put("SplitPane.background", c.bg); put("SplitPane.dividerFocusColor", c.line);
        put("Spinner.background", c.bgAlt); put("Spinner.foreground", c.fg);
        UIManager.put("Spinner.border", new RoundBorder(c.line, radius()));
    }}

    private static void put(String key, Color c) {{ UIManager.put(key, new ColorUIResource(c)); }}

    // ---------- factories ----------

    public static JLabel label(String text, Role role) {{
        JLabel l = new JLabel(role == Role.LABEL && uppercase() ? text.toUpperCase() : text);
        Palette c = colors();
        switch (role) {{
            case H1: l.setFont(font("display", "h2", Font.PLAIN).deriveFont((float) Math.min(px("h2"), 48))); l.setForeground(c.fg); break;
            case H2: l.setFont(font("display", "h3", Font.PLAIN).deriveFont((float) Math.round((Math.min(px("h2"), 48) + px("h3")) / 2.0))); l.setForeground(c.fg); break;
            case H3: l.setFont(font("strong", "h3", Font.BOLD)); l.setForeground(c.fg); break;
            case LABEL: l.setFont(font("strong", "label", Font.BOLD)); l.setForeground(c.fgMuted); break;
            case MUTED: l.setForeground(c.fgMuted); break;
            case FAINT: l.setForeground(c.fgFaint); break;
            case MONO: l.setFont(font("mono", "small", Font.PLAIN)); l.setForeground(c.fgDim); break;
            case STAT: l.setFont(font("display", "stat", Font.PLAIN)); l.setForeground(c.fg); break;
            default: l.setForeground(c.fgDim);
        }}
        return l;
    }}

    public static JButton button(String text, Kind kind) {{
        JButton b = new JButton(uppercase() ? text.toUpperCase() : text);
        b.setUI(new MonoButtonUI(kind));
        b.setFont(font("strong", "label", Font.BOLD));
        b.setRolloverEnabled(true);
        b.setFocusPainted(false);
        b.setContentAreaFilled(false);
        b.setBorder(new EmptyBorder(0, 16, 0, 16));
        b.setPreferredSize(new Dimension(b.getPreferredSize().width + 24, {ints(lambda v: data[v]["control"]["height"])}));
        return b;
    }}

    /** A raised panel with the surface colour, a border and the large radius. */
    public static JPanel card() {{
        JPanel p = new JPanel() {{
            @Override protected void paintComponent(Graphics g) {{
                Graphics2D g2 = (Graphics2D) g.create();
                g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                int r = radiusLarge() * 2;
                g2.setColor(colors().surface);
                g2.fill(new RoundRectangle2D.Float(0, 0, getWidth() - 1, getHeight() - 1, r, r));
                g2.setColor(colors().line);
                g2.draw(new RoundRectangle2D.Float(0, 0, getWidth() - 1, getHeight() - 1, r, r));
                g2.dispose();
            }}
        }};
        p.setOpaque(false);
        p.setBorder(new EmptyBorder(14, 16, 14, 16));
        return p;
    }}

    // ---------- painting helpers ----------

    /** Line border with optional rounded corners (radius 0 = square). */
    public static final class RoundBorder extends AbstractBorder {{
        private final Color color; private final int radius;
        public RoundBorder(Color color, int radius) {{ this.color = color; this.radius = radius; }}
        @Override public void paintBorder(Component c, Graphics g, int x, int y, int w, int h) {{
            Graphics2D g2 = (Graphics2D) g.create();
            g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            g2.setColor(c.hasFocus() ? colors().focus : color);
            g2.draw(new RoundRectangle2D.Float(x, y, w - 1, h - 1, radius * 2, radius * 2));
            g2.dispose();
        }}
        @Override public Insets getBorderInsets(Component c) {{ return new Insets(2, 2, 2, 2); }}
    }}

    static final class MonoButtonUI extends BasicButtonUI {{
        private final Kind kind;
        MonoButtonUI(Kind kind) {{ this.kind = kind; }}
        @Override public void paint(Graphics g, JComponent comp) {{
            AbstractButton b = (AbstractButton) comp;
            ButtonModel m = b.getModel();
            Palette c = colors();
            Graphics2D g2 = (Graphics2D) g.create();
            g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            float r = radius() * 2;
            RoundRectangle2D shape = new RoundRectangle2D.Float(0.5f, 0.5f, b.getWidth() - 1, b.getHeight() - 1, r, r);
            Color fill = null, border, text;
            boolean hover = m.isRollover(), on = b.isEnabled();
            switch (kind) {{
                case FILL: fill = hover ? c.accentHover : c.accent; border = fill; text = c.onAccent; break;
                case LINE: fill = hover ? c.surface : null; border = hover ? c.fg : c.lineStrong; text = c.fg; break;
                case GHOST: fill = hover ? c.surface : null; border = null; text = hover ? c.fg : c.fgMuted; break;
                default: fill = hover ? c.surface : null; border = c.fg; text = c.fg;
            }}
            if (!on) {{ fill = null; border = c.line; text = c.disabled; }}
            if (m.isPressed() && on && kind != Kind.FILL) fill = c.surfaceAlt;
            if (fill != null) {{ g2.setColor(fill); g2.fill(shape); }}
            if (border != null) {{ g2.setColor(border); g2.draw(shape); }}
            g2.dispose();
            b.setForeground(text);
            super.paint(g, comp);
        }}
        @Override protected void paintText(Graphics g, AbstractButton b, Rectangle r, String text) {{
            Graphics2D g2 = (Graphics2D) g;
            g2.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);
            g2.setColor(b.getForeground());
            FontMetrics fm = g2.getFontMetrics();
            g2.drawString(text, r.x, r.y + fm.getAscent());
        }}
    }}

    static final class CheckIcon implements Icon {{
        private final boolean radio;
        CheckIcon(boolean radio) {{ this.radio = radio; }}
        @Override public int getIconWidth() {{ return 16; }}
        @Override public int getIconHeight() {{ return 16; }}
        @Override public void paintIcon(Component comp, Graphics g, int x, int y) {{
            AbstractButton b = (AbstractButton) comp;
            boolean sel = b.isSelected();
            Palette c = colors();
            Graphics2D g2 = (Graphics2D) g.create();
            g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            g2.translate(x, y);
            if (radio) {{
                g2.setColor(c.bgAlt); g2.fillOval(0, 0, 15, 15);
                g2.setColor(sel ? c.fg : c.lineStrong); g2.drawOval(0, 0, 15, 15);
                if (sel) {{ g2.setColor(c.fgStrong); g2.fillOval(4, 4, 8, 8); }}
            }} else {{
                int r = radius() == 0 ? 0 : 8;
                g2.setColor(sel ? c.accent : c.bgAlt); g2.fillRoundRect(0, 0, 15, 15, r, r);
                g2.setColor(sel ? c.accent : c.lineStrong); g2.drawRoundRect(0, 0, 15, 15, r, r);
                if (sel) {{
                    g2.setColor(c.onAccent);
                    g2.setStroke(new BasicStroke(2f, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
                    g2.drawPolyline(new int[]{{4, 7, 12}}, new int[]{{8, 11, 5}}, 3);
                }}
            }}
            g2.dispose();
        }}
    }}
}}
'''
    p = o / "swing" / "monoui" / "MonoUI.java"
    write(p, text)
    return p


# ---------------------------------------------------------------- egui

def rgb(hexv: str) -> str:
    h = hexv.lstrip("#")
    return f"egui::Color32::from_rgb(0x{h[0:2]}, 0x{h[2:4]}, 0x{h[4:6]})"


def egui(o: Path, data: dict) -> Path:
    VS = list(data)
    E = lambda v: f"Variant::{v.capitalize()}"
    def pal(v):
        c = data[v]["color"]
        return "\n".join(f"        {snake(k)}: {rgb(c[k])}," for k in ROLES)
    pals = "\n".join("pub const %s: Palette = Palette {\n%s\n};\n" % (v.upper(), pal(v)) for v in VS)
    text = f'''// mono-ui for egui / eframe. {HEADER}
//
//   mono_egui::apply(ctx, mono_egui::Variant::Round);           // or Square, Blend, Paper
//   mono_egui::load_fonts(ctx, mono_egui::Variant::Round, "mono-ui/fonts/ttf");   // optional
//   if mono_egui::button_fill(ui, "Save").clicked() {{ ... }}
#![allow(dead_code)]

use eframe::egui;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Variant {{ {", ".join(v.capitalize() for v in VS)} }}

#[derive(Clone, Copy, Debug)]
pub struct Palette {{
{chr(10).join(f"    pub {snake(k)}: egui::Color32," for k in ROLES)}
}}

{pals}
pub fn palette(v: Variant) -> &'static Palette {{
    match v {{ {", ".join(f"{E(v)} => &{v.upper()}" for v in VS)} }}
}}

fn radius(v: Variant) -> (u8, u8, u8) {{
    match v {{
{chr(10).join(f'        {E(v)} => ({data[v]["radius"]["sm"]}, {data[v]["radius"]["md"]}, {data[v]["radius"]["lg"]}),' for v in VS)}
    }}
}}

fn uppercase(v: Variant) -> bool {{
    match v {{ {", ".join(f'{E(v)} => {str(data[v]["label"]["uppercase"]).lower()}' for v in VS)} }}
}}

fn light(v: Variant) -> bool {{
    match v {{ {", ".join(f'{E(v)} => {str(data[v]["light"]).lower()}' for v in VS)} }}
}}

fn variant_id() -> egui::Id {{ egui::Id::unique("mono_ui_variant") }}

/// Theme the whole context.
pub fn apply(ctx: &egui::Context, v: Variant) {{
    let c = palette(v);
    let (sm, md, lg) = radius(v);
    let mut vis = if light(v) {{ egui::Visuals::light() }} else {{ egui::Visuals::dark() }};
    vis.dark_mode = !light(v);
    vis.override_text_color = Some(c.fg);
    vis.panel_fill = c.bg;
    vis.window_fill = c.surface;
    vis.extreme_bg_color = c.bg_alt;
    vis.faint_bg_color = c.surface;
    vis.code_bg_color = c.surface;
    vis.window_stroke = egui::Stroke::new(1.0, c.line_strong);
    vis.window_corner_radius = egui::CornerRadius::same(lg);
    vis.menu_corner_radius = egui::CornerRadius::same(md);
    vis.window_shadow = egui::epaint::Shadow::NONE;
    vis.popup_shadow = egui::epaint::Shadow::NONE;
    vis.selection.bg_fill = c.selection;
    vis.selection.stroke = egui::Stroke::new(1.0, c.on_selection);
    vis.hyperlink_color = c.fg_strong;
    vis.warn_fg_color = c.fg_dim;
    vis.error_fg_color = c.fg_strong;
    vis.slider_trailing_fill = true;
    vis.handle_shape = if md == 0 {{ egui::style::HandleShape::Rect {{ aspect_ratio: 1.0 }} }} else {{ egui::style::HandleShape::Circle }};
    let r = egui::CornerRadius::same(md);
    let w = &mut vis.widgets;
    w.noninteractive.bg_fill = c.bg;
    w.noninteractive.weak_bg_fill = c.bg;
    w.noninteractive.bg_stroke = egui::Stroke::new(1.0, c.line);
    w.noninteractive.fg_stroke = egui::Stroke::new(1.0, c.fg_dim);
    w.noninteractive.corner_radius = r;
    w.inactive.bg_fill = c.bg_alt;
    w.inactive.weak_bg_fill = c.bg;
    w.inactive.bg_stroke = egui::Stroke::new(1.0, c.line_strong);
    w.inactive.fg_stroke = egui::Stroke::new(1.0, c.fg);
    w.inactive.corner_radius = r;
    w.hovered.bg_fill = c.surface;
    w.hovered.weak_bg_fill = c.surface;
    w.hovered.bg_stroke = egui::Stroke::new(1.0, c.fg);
    w.hovered.fg_stroke = egui::Stroke::new(1.0, c.fg_strong);
    w.hovered.corner_radius = r;
    w.hovered.expansion = 0.0;
    w.active.bg_fill = c.surface_alt;
    w.active.weak_bg_fill = c.surface_alt;
    w.active.bg_stroke = egui::Stroke::new(1.0, c.fg_strong);
    w.active.fg_stroke = egui::Stroke::new(1.0, c.fg_strong);
    w.active.corner_radius = r;
    w.active.expansion = 0.0;
    w.open = w.active;
    let _ = sm;
    let theme = if light(v) {{ egui::Theme::Light }} else {{ egui::Theme::Dark }};
    ctx.data_mut(|d| d.insert_temp(variant_id(), v));
    ctx.set_theme(theme);
    ctx.set_visuals_of(theme, vis);
    ctx.style_mut_of(theme, |s| {{
        s.spacing.item_spacing = egui::vec2(10.0, 8.0);
        s.spacing.button_padding = egui::vec2(12.0, 5.0);
        s.spacing.window_margin = egui::Margin::same(14);
        s.spacing.interact_size.y = {{ let (_, md, _) = radius(v); if md == 0 {{ 30.0 }} else {{ 26.0 }} }};
        s.spacing.slider_rail_height = 2.0;
    }});
}}

/// Load the variant's fonts from mono-ui/fonts/ttf (sans as proportional, mono as monospace).
pub fn load_fonts(ctx: &egui::Context, v: Variant, ttf_dir: &str) {{
    let (sans, mono) = match v {{
{chr(10).join(f'        {E(v)} => ("{data[v]["fontFile"]["sans"]}", "{data[v]["fontFile"]["mono"]}"),' for v in VS)}
    }};
    let mut fonts = egui::FontDefinitions::default();
    for (name, file, family) in [("mono-sans", sans, egui::FontFamily::Proportional), ("mono-mono", mono, egui::FontFamily::Monospace)] {{
        if let Ok(bytes) = std::fs::read(std::path::Path::new(ttf_dir).join(file)) {{
            fonts.font_data.insert(name.to_owned(), std::sync::Arc::new(egui::FontData::from_owned(bytes)));
            fonts.families.entry(family).or_default().insert(0, name.to_owned());
        }}
    }}
    ctx.set_fonts(fonts);
}}

fn styled(ui: &mut egui::Ui, text: &str, fill: Option<egui::Color32>, stroke: egui::Color32, fg: egui::Color32) -> egui::Response {{
    let mut b = egui::Button::new(egui::RichText::new(text).color(fg)).stroke(egui::Stroke::new(1.0, stroke));
    if let Some(f) = fill {{ b = b.fill(f); }}
    ui.add(b)
}}

fn variant_of(ui: &egui::Ui) -> Variant {{
    ui.ctx().data(|d| d.get_temp::<Variant>(variant_id())).unwrap_or(Variant::Round)
}}

pub fn button_fill(ui: &mut egui::Ui, text: &str) -> egui::Response {{
    let c = palette(variant_of(ui));
    styled(ui, text, Some(c.accent), c.accent, c.on_accent)
}}
pub fn button_line(ui: &mut egui::Ui, text: &str) -> egui::Response {{
    let c = palette(variant_of(ui));
    styled(ui, text, Some(egui::Color32::TRANSPARENT), c.line_strong, c.fg)
}}
pub fn button_ghost(ui: &mut egui::Ui, text: &str) -> egui::Response {{
    let c = palette(variant_of(ui));
    styled(ui, text, Some(egui::Color32::TRANSPARENT), egui::Color32::TRANSPARENT, c.fg_muted)
}}

/// Small muted label; uppercase in the variants that want it.
pub fn label(ui: &mut egui::Ui, text: &str) -> egui::Response {{
    let v = variant_of(ui);
    let t = if uppercase(v) {{ text.to_uppercase() }} else {{ text.to_owned() }};
    ui.label(egui::RichText::new(t).size({data["round"]["size"]["label"]}.0 + 1.0).color(palette(v).fg_muted).strong())
}}
pub fn heading(ui: &mut egui::Ui, text: &str) -> egui::Response {{
    let c = palette(variant_of(ui));
    ui.label(egui::RichText::new(text).size(32.0).color(c.fg))
}}
pub fn muted(ui: &mut egui::Ui, text: &str) -> egui::Response {{
    let c = palette(variant_of(ui));
    ui.label(egui::RichText::new(text).color(c.fg_muted))
}}

/// Thin progress bar in the foreground colour (egui's default uses the selection colour).
pub fn progress(ui: &mut egui::Ui, value: f32, width: f32) -> egui::Response {{
    let v = variant_of(ui);
    ui.add(egui::ProgressBar::new(value).desired_width(width).desired_height(4.0)
        .fill(palette(v).fg).corner_radius(egui::CornerRadius::same(radius(v).0)))
}}

/// A bordered card frame.
pub fn card(ui: &egui::Ui) -> egui::Frame {{
    let v = variant_of(ui);
    let c = palette(v);
    egui::Frame::new().fill(c.surface).stroke(egui::Stroke::new(1.0, c.line))
        .corner_radius(egui::CornerRadius::same(radius(v).2)).inner_margin(egui::Margin::same(14))
}}
'''
    p = o / "egui" / "mono_egui.rs"
    write(p, text)
    return p


# ---------------------------------------------------------------- iced

def iced(o: Path, data: dict) -> Path:
    VS = list(data)
    E = lambda v: f"Variant::{v.capitalize()}"
    def col(hexv):
        h = hexv.lstrip("#")
        return f"Color::from_rgb8(0x{h[0:2]}, 0x{h[2:4]}, 0x{h[4:6]})"
    def pal(v):
        c = data[v]["color"]
        return "\n".join(f"        {snake(k)}: {col(c[k])}," for k in ROLES)
    pals = "\n".join("pub const %s: Palette = Palette {\n%s\n};\n" % (v.upper(), pal(v)) for v in VS)
    def dfont(v):
        f = f'iced::Font::with_name("{data[v]["font"]["display"]}")'
        if data[v]["weight"]["display"] == 300:
            f = "iced::Font { weight: iced::font::Weight::Light, ..%s }" % f
        return f"        {E(v)} => {f},"
    display_fonts = "\n".join(dfont(v) for v in VS)
    text = f'''// mono-ui for iced. {HEADER}
//
//   fn theme(&self) -> iced::Theme {{ mono_iced::theme(mono_iced::Variant::Round) }}   // or Square, Blend, Paper
//   button("Save").style(mono_iced::button_fill)
#![allow(dead_code)]

use iced::widget::{{button, container}};
use iced::{{border, Background, Border, Color, Theme}};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Variant {{ {", ".join(v.capitalize() for v in VS)} }}

pub const VARIANTS: [Variant; {len(VS)}] = [{", ".join(E(v) for v in VS)}];

#[derive(Clone, Copy, Debug)]
pub struct Palette {{
{chr(10).join(f"    pub {snake(k)}: Color," for k in ROLES)}
}}

{pals}
pub fn palette(v: Variant) -> &'static Palette {{
    match v {{ {", ".join(f"{E(v)} => &{v.upper()}" for v in VS)} }}
}}

pub fn radius(v: Variant) -> f32 {{
    match v {{ {", ".join(f'{E(v)} => {data[v]["radius"]["md"]}.0' for v in VS)} }}
}}

pub fn radius_large(v: Variant) -> f32 {{
    match v {{ {", ".join(f'{E(v)} => {data[v]["radius"]["lg"]}.0' for v in VS)} }}
}}

/// Labels and button text are uppercase in this variant.
pub fn uppercase(v: Variant) -> bool {{
    match v {{ {", ".join(f'{E(v)} => {str(data[v]["label"]["uppercase"]).lower()}' for v in VS)} }}
}}

pub fn name(v: Variant) -> &'static str {{
    match v {{ {", ".join(f'{E(v)} => "Mono {v.capitalize()}"' for v in VS)} }}
}}

/// Font family for the variant. Load the TTF first with `.font(include_bytes!(..))` on the application;
/// `font_file(v)` gives the file name inside mono-ui/fonts/ttf.
pub fn font(v: Variant) -> iced::Font {{
    match v {{
{chr(10).join(f'        {E(v)} => iced::Font::with_name("{data[v]["font"]["sans"]}"),' for v in VS)}
    }}
}}
pub fn display_font(v: Variant) -> iced::Font {{
    match v {{
{display_fonts}
    }}
}}
pub fn font_file(v: Variant) -> &'static str {{
    match v {{ {", ".join(f'{E(v)} => "{data[v]["fontFile"]["sans"]}"' for v in VS)} }}
}}

/// The iced Theme for a variant. Built-in widgets pick up these colours.
pub fn theme(v: Variant) -> Theme {{
    let c = palette(v);
    Theme::custom(
        name(v).to_owned(),
        iced::theme::Palette {{
            background: c.bg,
            text: c.fg,
            primary: c.accent,
            success: c.fg_dim,
            warning: c.fg_dim,
            danger: c.fg_strong,
        }},
    )
}}

fn variant_of(theme: &Theme) -> Variant {{
    let n = theme.to_string();
    VARIANTS.into_iter().find(|v| name(*v) == n).unwrap_or(Variant::Round)
}}

fn btn(theme: &Theme, status: button::Status, fill: Option<Color>, hover: Option<Color>, stroke: Option<Color>, fg: Color) -> button::Style {{
    let v = variant_of(theme);
    let c = palette(v);
    let hovered = matches!(status, button::Status::Hovered | button::Status::Pressed);
    let disabled = matches!(status, button::Status::Disabled);
    let bg = if disabled {{ None }} else if hovered {{ hover.or(fill) }} else {{ fill }};
    button::Style {{
        background: bg.map(Background::Color),
        text_color: if disabled {{ c.disabled }} else {{ fg }},
        border: Border {{
            color: if disabled {{ c.line }} else {{ stroke.unwrap_or(Color::TRANSPARENT) }},
            width: 1.0,
            radius: border::radius(radius(v)),
        }},
        ..button::Style::default()
    }}
}}

pub fn button_fill(theme: &Theme, status: button::Status) -> button::Style {{
    let c = palette(variant_of(theme));
    btn(theme, status, Some(c.accent), Some(c.accent_hover), Some(c.accent), c.on_accent)
}}
pub fn button_outline(theme: &Theme, status: button::Status) -> button::Style {{
    let c = palette(variant_of(theme));
    btn(theme, status, None, Some(c.surface), Some(c.fg), c.fg)
}}
pub fn button_line(theme: &Theme, status: button::Status) -> button::Style {{
    let c = palette(variant_of(theme));
    let hovered = matches!(status, button::Status::Hovered);
    btn(theme, status, None, Some(c.surface), Some(if hovered {{ c.fg }} else {{ c.line_strong }}), c.fg)
}}
pub fn button_ghost(theme: &Theme, status: button::Status) -> button::Style {{
    let c = palette(variant_of(theme));
    let hovered = matches!(status, button::Status::Hovered);
    btn(theme, status, None, Some(c.surface), None, if hovered {{ c.fg }} else {{ c.fg_muted }})
}}

/// Raised card: surface fill, line border, large radius.
pub fn card(theme: &Theme) -> container::Style {{
    let v = variant_of(theme);
    let c = palette(v);
    container::Style {{
        background: Some(Background::Color(c.surface)),
        border: Border {{ color: c.line, width: 1.0, radius: border::radius(radius_large(v)) }},
        ..container::Style::default()
    }}
}}

/// Bordered strip, no fill (the stats row).
pub fn outlined(theme: &Theme) -> container::Style {{
    let v = variant_of(theme);
    let c = palette(v);
    container::Style {{
        border: Border {{ color: c.line, width: 1.0, radius: border::radius(radius(v)) }},
        ..container::Style::default()
    }}
}}
'''
    p = o / "iced" / "mono_iced.rs"
    write(p, text)
    return p


# ---------------------------------------------------------------- Fyne

def fyne(o: Path, data: dict) -> Path:
    VS = list(data)
    gname = lambda k: snake(k).title().replace("_", "")
    w = max(len(gname(k)) for k in ROLES)
    def nrgba(hexv):
        h = hexv.lstrip("#")
        return f"color.NRGBA{{R: 0x{h[0:2]}, G: 0x{h[2:4]}, B: 0x{h[4:6]}, A: 0xff}}"
    def pal(v):
        c = data[v]["color"]
        return "\n".join(f"\t\t{(gname(k) + ':'):<{w + 1}} {nrgba(c[k])}," for k in ROLES)
    fields = "\n".join(f"\t{gname(k):<{w}} color.NRGBA" for k in ROLES)  # aligned the way gofmt wants
    pals = "\n".join("\t%s: {\n%s\n\t}," % (v.capitalize(), pal(v)) for v in VS)
    text = f'''// mono-ui for Fyne (fyne.io/fyne/v2). {HEADER}
//
//	a := app.New()
//	a.Settings().SetTheme(monotheme.New(monotheme.Round))   // or Square, Blend, Paper
package monotheme

import (
	"image/color"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/theme"
)

type Variant int

const (
	{VS[0].capitalize()} Variant = iota
{chr(10).join(chr(9) + v.capitalize() for v in VS[1:])}
)

// Palette holds every mono colour role.
type Palette struct {{
{fields}
}}

var palettes = map[Variant]Palette{{
{pals}
}}

var radii = map[Variant]float32{{{", ".join(f'{v.capitalize()}: {data[v]["radius"]["md"]}' for v in VS)}}}

var textSizes = map[Variant]float32{{{", ".join(f'{v.capitalize()}: {data[v]["size"]["ui"]}' for v in VS)}}}

var lightVariants = map[Variant]bool{{{", ".join(f'{v.capitalize()}: {str(data[v]["light"]).lower()}' for v in VS)}}}

// Colors returns the palette for a variant.
func Colors(v Variant) Palette {{ return palettes[v] }}

type monoTheme struct {{
	v Variant
	c Palette
}}

// New returns a fyne.Theme for the variant. Fonts come from the default theme unless you
// embed mono-ui's TTFs with fyne bundle and return them from Font().
func New(v Variant) fyne.Theme {{ return &monoTheme{{v: v, c: palettes[v]}} }}

func (m *monoTheme) Color(n fyne.ThemeColorName, _ fyne.ThemeVariant) color.Color {{
	c := m.c
	switch n {{
	case theme.ColorNameBackground:
		return c.Bg
	case theme.ColorNameForeground:
		return c.Fg
	case theme.ColorNameButton:
		return c.Surface
	case theme.ColorNameDisabledButton:
		return c.Bg
	case theme.ColorNameDisabled:
		return c.Disabled
	case theme.ColorNameInputBackground:
		return c.BgAlt
	case theme.ColorNameInputBorder:
		return c.Line
	case theme.ColorNamePlaceHolder:
		return c.FgFaint
	case theme.ColorNamePrimary, theme.ColorNameFocus:
		return c.Accent
	case theme.ColorNameForegroundOnPrimary:
		return c.OnAccent
	case theme.ColorNameHover:
		return c.Surface
	case theme.ColorNamePressed:
		return c.SurfaceAlt
	case theme.ColorNameSelection:
		return c.Selection
	case theme.ColorNameSeparator:
		return c.Line
	case theme.ColorNameScrollBar:
		return c.LineStrong
	case theme.ColorNameShadow:
		return color.NRGBA{{A: 0x40}}
	case theme.ColorNameMenuBackground, theme.ColorNameOverlayBackground:
		return c.Surface
	case theme.ColorNameHeaderBackground:
		return c.BgAlt
	case theme.ColorNameHyperlink:
		return c.FgStrong
	case theme.ColorNameError:
		return c.FgStrong
	case theme.ColorNameSuccess, theme.ColorNameWarning:
		return c.FgDim
	}}
	if lightVariants[m.v] {{
		return theme.DefaultTheme().Color(n, theme.VariantLight)
	}}
	return theme.DefaultTheme().Color(n, theme.VariantDark)
}}

func (m *monoTheme) Font(s fyne.TextStyle) fyne.Resource {{ return theme.DefaultTheme().Font(s) }}

func (m *monoTheme) Icon(n fyne.ThemeIconName) fyne.Resource {{ return theme.DefaultTheme().Icon(n) }}

func (m *monoTheme) Size(n fyne.ThemeSizeName) float32 {{
	switch n {{
	case theme.SizeNameInputRadius, theme.SizeNameSelectionRadius:
		return radii[m.v]
	case theme.SizeNameInputBorder:
		return 1
	case theme.SizeNameText:
		return textSizes[m.v]
	}}
	return theme.DefaultTheme().Size(n)
}}
'''
    p = o / "fyne" / "monotheme" / "theme.go"
    write(p, text)
    return p


# ---------------------------------------------------------------- Avalonia

def avalonia(o: Path, data: dict) -> list[Path]:
    files = []
    for v in data:
        c, d = data[v]["color"], data[v]
        r = d["radius"]
        brushes = "\n".join(f'    <SolidColorBrush x:Key="Mono{k[0].upper() + k[1:]}Brush" Color="{c[k]}" />' for k in ROLES)
        axaml = f'''<!-- Mono {v} for Avalonia (Fluent theme). {HEADER.replace("--", "-")}
     App.axaml:  <Application.Styles><FluentTheme /><StyleInclude Source="avares://YourApp/Mono{v.capitalize()}.axaml" /></Application.Styles>
     and set RequestedThemeVariant="{"Light" if data[v]["light"] else "Dark"}". -->
<Styles xmlns="https://github.com/avaloniaui" xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <Styles.Resources>
    <ResourceDictionary>
{brushes}
      <CornerRadius x:Key="ControlCornerRadius">{r["md"]}</CornerRadius>
      <CornerRadius x:Key="OverlayCornerRadius">{r["lg"]}</CornerRadius>
      <FontFamily x:Key="ContentControlThemeFontFamily">{d["font"]["sans"]}</FontFamily>
      <Color x:Key="SystemAccentColor">{c["accent"]}</Color>
      <Color x:Key="SystemAccentColorLight1">{c["accentHover"]}</Color>
      <Color x:Key="SystemAccentColorDark1">{c["fgMuted"]}</Color>
      <SolidColorBrush x:Key="SystemControlBackgroundAltHighBrush" Color="{c["bg"]}" />
      <SolidColorBrush x:Key="SystemControlForegroundBaseHighBrush" Color="{c["fg"]}" />
      <SolidColorBrush x:Key="SystemControlForegroundBaseMediumBrush" Color="{c["fgMuted"]}" />
      <SolidColorBrush x:Key="TextControlBackground" Color="{c["bgAlt"]}" />
      <SolidColorBrush x:Key="TextControlBackgroundPointerOver" Color="{c["bgAlt"]}" />
      <SolidColorBrush x:Key="TextControlBackgroundFocused" Color="{c["bgAlt"]}" />
      <SolidColorBrush x:Key="TextControlBorderBrush" Color="{c["line"]}" />
      <SolidColorBrush x:Key="TextControlBorderBrushPointerOver" Color="{c["lineStrong"]}" />
      <SolidColorBrush x:Key="TextControlBorderBrushFocused" Color="{c["focus"]}" />
      <SolidColorBrush x:Key="ButtonBackground" Color="Transparent" />
      <SolidColorBrush x:Key="ButtonBackgroundPointerOver" Color="{c["surface"]}" />
      <SolidColorBrush x:Key="ButtonBackgroundPressed" Color="{c["surfaceAlt"]}" />
      <SolidColorBrush x:Key="ButtonForeground" Color="{c["fg"]}" />
      <SolidColorBrush x:Key="ButtonBorderBrush" Color="{c["fg"]}" />
      <SolidColorBrush x:Key="ButtonBorderBrushPointerOver" Color="{c["fg"]}" />
    </ResourceDictionary>
  </Styles.Resources>

  <Style Selector="Window"><Setter Property="Background" Value="{{StaticResource MonoBgBrush}}" /></Style>
  <Style Selector="TextBlock.h1"><Setter Property="FontSize" Value="{min(d["size"]["h2"], 48)}" /><Setter Property="Foreground" Value="{{StaticResource MonoFgBrush}}" /><Setter Property="FontFamily" Value="{d["font"]["display"]}" /><Setter Property="FontWeight" Value="{d["weight"]["display"]}" /></Style>
  <Style Selector="TextBlock.h3"><Setter Property="FontSize" Value="{d["size"]["h3"]}" /><Setter Property="Foreground" Value="{{StaticResource MonoFgBrush}}" /><Setter Property="FontWeight" Value="SemiBold" /></Style>
  <Style Selector="TextBlock.label"><Setter Property="FontSize" Value="{d["size"]["label"]}" /><Setter Property="Foreground" Value="{{StaticResource MonoFgMutedBrush}}" /><Setter Property="FontWeight" Value="Bold" /></Style>
  <Style Selector="TextBlock.muted"><Setter Property="Foreground" Value="{{StaticResource MonoFgMutedBrush}}" /></Style>
  <Style Selector="TextBlock.faint"><Setter Property="Foreground" Value="{{StaticResource MonoFgFaintBrush}}" /></Style>
  <Style Selector="Button"><Setter Property="BorderThickness" Value="1" /><Setter Property="Padding" Value="{d["control"]["padX"]},{(d["control"]["height"] - 18) // 2}" /></Style>
  <Style Selector="Button.fill"><Setter Property="Background" Value="{{StaticResource MonoAccentBrush}}" /><Setter Property="Foreground" Value="{{StaticResource MonoOnAccentBrush}}" /><Setter Property="BorderBrush" Value="{{StaticResource MonoAccentBrush}}" /></Style>
  <Style Selector="Button.fill:pointerover /template/ ContentPresenter"><Setter Property="Background" Value="{{StaticResource MonoAccentHoverBrush}}" /><Setter Property="Foreground" Value="{{StaticResource MonoOnAccentBrush}}" /></Style>
  <Style Selector="Button.line"><Setter Property="BorderBrush" Value="{{StaticResource MonoLineStrongBrush}}" /></Style>
  <Style Selector="Button.ghost"><Setter Property="BorderBrush" Value="Transparent" /><Setter Property="Foreground" Value="{{StaticResource MonoFgMutedBrush}}" /></Style>
  <Style Selector="Border.card"><Setter Property="Background" Value="{{StaticResource MonoSurfaceBrush}}" /><Setter Property="BorderBrush" Value="{{StaticResource MonoLineBrush}}" /><Setter Property="BorderThickness" Value="1" /><Setter Property="CornerRadius" Value="{r["lg"]}" /><Setter Property="Padding" Value="16,14" /></Style>
</Styles>
'''
        p = o / "avalonia" / f"Mono{v.capitalize()}.axaml"
        write(p, axaml)
        files.append(p)
    return files
