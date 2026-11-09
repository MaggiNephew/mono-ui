// mono-ui GTK demo in D.
//   dub run -- round
//   dub run -- square
//   dub run -- round --shot out.png
import gtkmin;
import monoui.gtk;
import std.string : toStringz;

__gshared GtkWidget* win;
__gshared string shotPath;

GtkWidget* label(string text, string cls = null)
{
    auto l = gtk_label_new(text.toStringz);
    gtk_label_set_xalign(l, 0);
    if (cls) addClass(l, cls);
    return l;
}

GtkWidget* button(string text, string cls = null)
{
    auto b = gtk_button_new_with_label(text.toStringz);
    if (cls) addClass(b, cls);
    return b;
}

GtkWidget* stats(string[2][] items)
{
    auto box = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 0);
    addClass(box, "stats");
    foreach (it; items)
    {
        auto cell = gtk_box_new(GTK_ORIENTATION_VERTICAL, 2);
        addClass(cell, "cell");
        gtk_box_pack_start(cell, label(it[0], "stat"), 0, 0, 0);
        gtk_box_pack_start(cell, label(it[1], "label"), 0, 0, 0);
        gtk_box_pack_start(box, cell, 1, 1, 0);
    }
    return box;
}

void pack(GtkWidget* box, GtkWidget* child, bool expand = false)
{
    gtk_box_pack_start(box, child, expand, true, 0);
}

extern (C) int takeShot(void*) nothrow
{
    auto w = gtk_widget_get_window(win);
    auto pb = gdk_pixbuf_get_from_window(w, 0, 0, gdk_window_get_width(w), gdk_window_get_height(w));
    gdk_pixbuf_save(pb, shotPath.toStringz, "png", null, null);
    gtk_main_quit();
    return 0;
}

void main(string[] args)
{
    int argc = 0;
    gtk_init(&argc, null);
    Variant variant = Variant.round;
    foreach (i, a; args)
    {
        static foreach (m; __traits(allMembers, Variant))
            if (a == m) variant = __traits(getMember, Variant, m);
        if (a == "--shot" && i + 1 < args.length) shotPath = args[i + 1];
    }
    import std.file : thisExePath;
    import std.path : buildNormalizedPath, dirName;
    import std.process : environment;
    // the demo binary lives in mono-ui/examples/d-gtk; fonts are in mono-ui/fonts/ttf
    const fonts = environment.get("MONO_UI_FONTS", buildNormalizedPath(thisExePath.dirName, "..", "..", "fonts", "ttf"));
    apply(variant, fonts);

    win = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(win, "mono-ui · GTK · D");
    gtk_window_set_default_size(win, 980, 660);
    g_signal_connect_data(win, "destroy", cast(GCallback)&gtk_main_quit, null, null, 0);

    auto outer = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 0);
    gtk_container_add(win, outer);

    // sidebar
    auto side = gtk_box_new(GTK_ORIENTATION_VERTICAL, 8);
    gtk_container_set_border_width(side, 16);
    gtk_widget_set_size_request(side, 200, -1);
    pack(side, label("Rice", "label"));
    auto list = gtk_list_box_new();
    foreach (i, name; ["Hyprland", "Quickshell bar", "Orbital lock", "Soundboard", "cyber"])
        gtk_list_box_insert(list, label(name), cast(int) i);
    gtk_list_box_select_row(list, gtk_list_box_get_row_at_index(list, 1));
    pack(side, list, true);
    pack(side, label("D · ldc2 · GTK 3", "mono"));
    pack(outer, side);
    pack(outer, gtk_separator_new(GTK_ORIENTATION_VERTICAL));

    // main column
    auto main = gtk_box_new(GTK_ORIENTATION_VERTICAL, 12);
    gtk_container_set_border_width(main, 24);
    pack(main, label("04 · Bar", "label"));
    pack(main, label("Quickshell bar", "h1"));
    pack(main, label("workspaces · clock · music line · stats · privacy light", "muted"));
    pack(main, stats([["5", "Workspaces"], ["41%", "CPU"], ["6.2", "GB used"], ["on", "Mic light"]]));

    auto row = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 8);
    pack(row, button("Reload bar", "fill"));
    pack(row, button("Edit shell.qml", "line"));
    pack(row, button("Outline"));
    pack(row, button("Ghost", "ghost"));
    auto off = button("Disabled");
    gtk_widget_set_sensitive(off, 0);
    pack(row, off);
    gtk_widget_set_halign(row, GTK_ALIGN_START);
    pack(main, row);

    auto tabs = gtk_notebook_new();
    auto form = gtk_box_new(GTK_ORIENTATION_VERTICAL, 10);
    gtk_container_set_border_width(form, 16);
    auto fields = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 16);
    auto f1 = gtk_box_new(GTK_ORIENTATION_VERTICAL, 6);
    pack(f1, label("Font", "label"));
    auto entry = gtk_entry_new();
    gtk_entry_set_text(entry, "3270 Nerd Font Mono");
    pack(f1, entry);
    pack(fields, f1, true);
    auto f2 = gtk_box_new(GTK_ORIENTATION_VERTICAL, 6);
    pack(f2, label("Position", "label"));
    auto combo = gtk_combo_box_text_new();
    foreach (s; ["Top", "Bottom"]) gtk_combo_box_text_append_text(combo, s.toStringz);
    gtk_combo_box_set_active(combo, 0);
    pack(f2, combo);
    pack(fields, f2);
    auto f3 = gtk_box_new(GTK_ORIENTATION_VERTICAL, 6);
    pack(f3, label("Height", "label"));
    auto spin = gtk_spin_button_new_with_range(16, 64, 1);
    gtk_spin_button_set_value(spin, 30);
    pack(f3, spin);
    pack(fields, f3);
    pack(form, fields);
    auto search = gtk_entry_new();
    gtk_entry_set_placeholder_text(search, "Search modules…");
    pack(form, search);

    auto checks = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 22);
    auto c1 = gtk_check_button_new_with_label("Music line");
    gtk_toggle_button_set_active(c1, 1);
    pack(checks, c1);
    pack(checks, gtk_check_button_new_with_label("Compact"));
    auto r1 = gtk_radio_button_new_with_label_from_widget(null, "Clock 24h");
    pack(checks, r1);
    pack(checks, gtk_radio_button_new_with_label_from_widget(r1, "Clock 12h"));
    auto sw = gtk_switch_new();
    gtk_switch_set_active(sw, 1);
    gtk_widget_set_valign(sw, GTK_ALIGN_CENTER);
    pack(checks, sw);
    pack(form, checks);

    auto sliders = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 24);
    auto scale = gtk_scale_new_with_range(GTK_ORIENTATION_HORIZONTAL, 0, 100, 1);
    gtk_scale_set_draw_value(scale, 0);
    gtk_range_set_value(scale, 62);
    pack(sliders, scale, true);
    auto bar = gtk_progress_bar_new();
    gtk_progress_bar_set_fraction(bar, 0.64);
    gtk_widget_set_valign(bar, GTK_ALIGN_CENTER);
    pack(sliders, bar, true);
    pack(form, sliders);
    gtk_notebook_append_page(tabs, form, gtk_label_new("Settings"));
    gtk_notebook_append_page(tabs, gtk_text_view_new(), gtk_label_new("shell.qml"));
    gtk_notebook_append_page(tabs, gtk_box_new(GTK_ORIENTATION_VERTICAL, 0), gtk_label_new("Logs"));
    pack(main, tabs, true);

    auto card = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 12);
    addClass(card, "card");
    auto ct = gtk_box_new(GTK_ORIENTATION_VERTICAL, 2);
    pack(ct, label("Update badge", "h3"));
    pack(ct, label("12 packages · safe-update ready", "muted"));
    pack(card, ct, true);
    auto run = button("Update", "fill");
    gtk_widget_set_valign(run, GTK_ALIGN_CENTER);
    pack(card, run);
    pack(main, card);

    pack(outer, main, true);
    gtk_widget_show_all(win);
    if (shotPath.length) g_timeout_add(600, &takeShot, null);
    gtk_main();
}
