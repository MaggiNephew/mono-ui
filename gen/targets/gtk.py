"""GTK 3: stylesheets for any GTK app, plus a dependency-free D module that installs them.

dist/gtk/mono-square.css, mono-round.css       load at GTK_STYLE_PROVIDER_PRIORITY_APPLICATION
dist/gtk/d/monoui/gtk.d                         D: monoui.gtk.apply(Variant.round); works with or without GtkD
dist/gtk/c/mono_gtk.h                           C: mono_gtk_apply(MONO_GTK_ROUND, NULL)
"""
from __future__ import annotations

from pathlib import Path
from string import Template

import json

from qt import icons, qss_values
from tokens import HEADER, ROOT, Tokens, fmt, write

TEMPLATE = ROOT / "gen" / "templates" / "gtk" / "gtk3.css"


def values(t: Tokens, v: str) -> dict[str, str]:
    vals = qss_values(t, v)
    d = t.v(v)
    vals["size_h1"] = vals["size_h2"]          # capped desktop h1
    vals["size_h2"] = vals["h2_qt"]
    lab = d["label"]
    vals["label_tracking_px"] = fmt(round(lab["tracking"] * d["size"]["label"], 2))
    vals["btn_tracking_px"] = fmt(round(lab["tracking"] * 0.64 * d["size"]["label"], 2))
    vals["fast"] = str(t.data["motion"]["fast"])
    vals["r_pill"] = str(min(d["radius"]["pill"], 999) if d["radius"]["md"] else 0)
    return vals


def build(t: Tokens, out: Path) -> list[Path]:
    o = out / "gtk"
    tpl = Template(TEMPLATE.read_text())
    css = {}
    files = []
    ic = {}
    for v in t.variants:
        vals = values(t, v)
        # the .css files reference icons next to them; the embedded copies get a path filled in at runtime
        p = o / f"mono-{v}.css"
        write(p, f"/* {HEADER} */\n" + tpl.substitute(vals, icons=f"icons/{v}"))
        files.append(p)
        css[v] = tpl.substitute(vals, icons="@MONO_ICONS@")
        ic[v] = icons(t, v)
        for name, svg in ic[v].items():
            ip = o / "icons" / v / name
            write(ip, svg + "\n")
            files.append(ip)
    files.append(d_module(t, o, css, ic))
    files.append(c_header(t, o, css, ic))
    return files


def d_module(t: Tokens, o: Path, css: dict[str, str], ic: dict) -> Path:
    d_icons = {v: "[" + ", ".join(f'[{json.dumps(n)}, {json.dumps(svg)}]' for n, svg in ic[v].items()) + "]" for v in ic}
    text = f"""// mono-ui for GTK 3 in D. {HEADER}
//
//   import monoui.gtk;
//   gtk_init(...);                         // or GtkD's Main.init(args)
//   monoui.gtk.apply(Variant.round);       // or square, blend, paper
//   addClass(widgetPtr, "fill");           // GtkD: addClass(button.getWidgetStruct(), "fill")
//
// No dependencies besides the GTK 3 and fontconfig C libraries (link: gtk-3 gdk-3 gobject-2.0 fontconfig).
module monoui.gtk;

import std.array : replace;
import std.file : dirEntries, exists, isDir, mkdirRecurse, readText, SpanMode, tempDir, write;
import std.path : buildPath;
import std.process : environment;
import std.string : toStringz;

enum Variant {{ {', '.join(t.variants)} }}

// private, so these names never clash with GtkD or your own bindings
private extern (C) nothrow @nogc
{{
    struct GtkCssProvider;
    struct GdkScreen;
    struct GtkWidget;
    struct GtkStyleContext;
    struct GError {{ uint domain; int code; char* message; }}
    struct FcConfig;
    GtkCssProvider* gtk_css_provider_new();
    int gtk_css_provider_load_from_data(GtkCssProvider*, const(char)*, ptrdiff_t, GError**);
    GdkScreen* gdk_screen_get_default();
    void gtk_style_context_add_provider_for_screen(GdkScreen*, void*, uint);
    void gtk_style_context_remove_provider_for_screen(GdkScreen*, void*);
    GtkStyleContext* gtk_widget_get_style_context(GtkWidget*);
    void gtk_style_context_add_class(GtkStyleContext*, const(char)*);
    void gtk_style_context_remove_class(GtkStyleContext*, const(char)*);
    void g_error_free(GError*);
    FcConfig* FcConfigGetCurrent();
    int FcConfigAppFontAddFile(FcConfig*, const(char)*);
}}

/// GTK_STYLE_PROVIDER_PRIORITY_APPLICATION
enum uint priorityApplication = 600;

/// The stylesheet text for a variant.
string css(Variant v)
{{
    return cssAll[cast(size_t) v];
}}

private __gshared GtkCssProvider* current;

/// Register the bundled TTFs (mono-ui/fonts/ttf) with fontconfig so GTK can use them.
/// Looks in `dir`, then $MONO_UI_FONTS. Returns how many files were added.
int loadFonts(string dir = null)
{{
    if (dir is null) dir = environment.get("MONO_UI_FONTS", null);
    if (dir is null || !exists(dir) || !isDir(dir)) return 0;
    int n;
    auto cfg = FcConfigGetCurrent();
    foreach (e; dirEntries(dir, "*.ttf", SpanMode.shallow))
        if (FcConfigAppFontAddFile(cfg, e.name.toStringz)) n++;
    return n;
}}

/// Theme every GTK widget on the default screen. Call after gtk_init. Safe to call again to switch variant.
bool apply(Variant v = Variant.round, string fontsDir = null)
{{
    loadFonts(fontsDir);
    auto screen = gdk_screen_get_default();
    if (screen is null) return false;
    if (current !is null) gtk_style_context_remove_provider_for_screen(screen, current);
    current = gtk_css_provider_new();
    const text = css(v).replace("@MONO_ICONS@", writeIcons(v));
    GError* err;
    if (!gtk_css_provider_load_from_data(current, text.ptr, cast(ptrdiff_t) text.length, &err))
    {{
        if (err) g_error_free(err);
        return false;
    }}
    gtk_style_context_add_provider_for_screen(screen, current, priorityApplication);
    return true;
}}

/// Write the variant's icons to a cache folder (GTK needs real files) and return its path.
string writeIcons(Variant v)
{{
    const base = environment.get("XDG_CACHE_HOME", buildPath(environment.get("HOME", tempDir), ".cache"));
    const dir = buildPath(base, "mono-ui-icons", variantNames[cast(size_t) v]);
    mkdirRecurse(dir);
    foreach (pair; iconsAll[cast(size_t) v])
    {{
        const path = buildPath(dir, pair[0]);
        if (!exists(path) || readText(path) != pair[1]) write(path, pair[1]);
    }}
    return dir;
}}

/// Add a mono-ui style class (h1, h2, h3, label, muted, faint, mono, stat, fill, line, ghost, card, stats, cell).
void addClass(void* widget, string cls)
{{
    gtk_style_context_add_class(gtk_widget_get_style_context(cast(GtkWidget*) widget), cls.toStringz);
}}

void removeClass(void* widget, string cls)
{{
    gtk_style_context_remove_class(gtk_widget_get_style_context(cast(GtkWidget*) widget), cls.toStringz);
}}

private immutable string[] variantNames = [{", ".join(json.dumps(v) for v in t.variants)}];
""" + "".join(f"""
private immutable string[2][] icons_{v} = {d_icons[v]};
private enum string css_{v} = q"MONOCSS
{css[v]}MONOCSS";
""" for v in t.variants) + f"""
private immutable string[2][][] iconsAll = [{", ".join(f"icons_{v}" for v in t.variants)}];
private immutable string[] cssAll = [{", ".join(f"css_{v}" for v in t.variants)}];
"""
    p = o / "d" / "monoui" / "gtk.d"
    write(p, text)
    return p


def c_str(s: str) -> str:
    lines = s.replace("\\", "\\\\").replace('"', '\\"').split("\n")
    return "\n".join(f'    "{ln}\\n"' for ln in lines)


def c_header(t: Tokens, o: Path, css: dict[str, str], ic: dict) -> Path:
    c_icons = {v: ",\n".join(f'    {{"{n}", "' + svg.replace('"', '\\"') + '"}' for n, svg in ic[v].items()) for v in ic}
    text = f"""/* mono-ui for GTK 3 in C. {HEADER}

   #include "mono_gtk.h"
   gtk_init(&argc, &argv);
   mono_gtk_apply(MONO_GTK_ROUND, NULL);       // or _SQUARE, _BLEND, _PAPER; optional fonts dir
   mono_gtk_add_class(button, "fill");
*/
#ifndef MONO_GTK_H
#define MONO_GTK_H

#include <gtk/gtk.h>
#include <fontconfig/fontconfig.h>

typedef enum {{ {", ".join(f"MONO_GTK_{v.upper()}" for v in t.variants)} }} MonoGtkVariant;
""" + "".join(f"""
static const char mono_gtk_css_{v}[] =
{c_str(css[v])};

static const char *const mono_gtk_icons_{v}[][2] = {{
{c_icons[v]}
}};
""" for v in t.variants) + f"""
static const char *const mono_gtk_names[] = {{ {", ".join(json.dumps(v) for v in t.variants)} }};
static const char *const mono_gtk_css[] = {{ {", ".join(f"mono_gtk_css_{v}" for v in t.variants)} }};
static const char *const (*const mono_gtk_icons[])[2] = {{ {", ".join(f"mono_gtk_icons_{v}" for v in t.variants)} }};
static const size_t mono_gtk_icon_counts[] = {{ {", ".join(f"G_N_ELEMENTS(mono_gtk_icons_{v})" for v in t.variants)} }};

/* GTK needs icon files on disk: write them to ~/.cache/mono-ui-icons/<variant>. Caller frees. */
static inline char *mono_gtk_write_icons(MonoGtkVariant v) {{
    const char *const (*icons)[2] = mono_gtk_icons[v];
    const size_t n = mono_gtk_icon_counts[v];
    char *dir = g_build_filename(g_get_user_cache_dir(), "mono-ui-icons", mono_gtk_names[v], NULL);
    g_mkdir_with_parents(dir, 0755);
    for (size_t i = 0; i < n; i++) {{
        char *path = g_build_filename(dir, icons[i][0], NULL);
        g_file_set_contents(path, icons[i][1], -1, NULL);
        g_free(path);
    }}
    return dir;
}}

static inline int mono_gtk_load_fonts(const char *dir) {{
    if (!dir) dir = g_getenv("MONO_UI_FONTS");
    if (!dir) return 0;
    GDir *d = g_dir_open(dir, 0, NULL);
    if (!d) return 0;
    int n = 0;
    const char *name;
    while ((name = g_dir_read_name(d))) {{
        if (!g_str_has_suffix(name, ".ttf")) continue;
        char *path = g_build_filename(dir, name, NULL);
        n += FcConfigAppFontAddFile(FcConfigGetCurrent(), (const FcChar8 *)path) ? 1 : 0;
        g_free(path);
    }}
    g_dir_close(d);
    return n;
}}

static inline gboolean mono_gtk_apply(MonoGtkVariant v, const char *fonts_dir) {{
    static GtkCssProvider *current = NULL;
    mono_gtk_load_fonts(fonts_dir);
    GdkScreen *screen = gdk_screen_get_default();
    if (!screen) return FALSE;
    if (current) {{ gtk_style_context_remove_provider_for_screen(screen, GTK_STYLE_PROVIDER(current)); g_object_unref(current); }}
    current = gtk_css_provider_new();
    char *dir = mono_gtk_write_icons(v);
    char **parts = g_strsplit(mono_gtk_css[v], "@MONO_ICONS@", -1);
    char *css = g_strjoinv(dir, parts);
    g_strfreev(parts);
    g_free(dir);
    const gboolean ok = gtk_css_provider_load_from_data(current, css, -1, NULL);
    g_free(css);
    if (!ok) return FALSE;
    gtk_style_context_add_provider_for_screen(screen, GTK_STYLE_PROVIDER(current), GTK_STYLE_PROVIDER_PRIORITY_APPLICATION);
    return TRUE;
}}

static inline void mono_gtk_add_class(GtkWidget *w, const char *cls) {{
    gtk_style_context_add_class(gtk_widget_get_style_context(w), cls);
}}

#endif
"""
    p = o / "c" / "mono_gtk.h"
    write(p, text)
    return p
