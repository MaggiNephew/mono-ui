"""Dear PyGui demo: python3 examples/dearpygui/demo.py [square|round|blend|paper]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "dist" / "apps" / "dearpygui"))
import dearpygui.dearpygui as dpg

import mono_dpg

variant = sys.argv[1] if len(sys.argv) > 1 else "round"
dpg.create_context()
t = mono_dpg.apply(variant)
up = (lambda s: s.upper()) if mono_dpg._DATA[variant]["label"]["uppercase"] else (lambda s: s)

with dpg.window(tag="main"):
    dpg.add_text(up("01 · Settings")); dpg.bind_item_theme(dpg.last_item(), t["muted"])
    dpg.add_text("Display")
    if "display" in t["fonts"]:
        dpg.bind_item_font(dpg.last_item(), t["fonts"]["display"])
    dpg.add_text("Changes apply after a restart."); dpg.bind_item_theme(dpg.last_item(), t["muted"])
    dpg.add_spacer(height=8)
    dpg.add_input_text(label=up("Name"), default_value="mono", width=280)
    dpg.add_combo(["square", "round", "blend", "paper"], label=up("Theme"), default_value=variant, width=280)
    dpg.add_checkbox(label="Show hidden files", default_value=True)
    dpg.add_radio_button(["Compact", "Comfortable"], horizontal=True)
    dpg.add_slider_int(label=up("Scale"), default_value=62, width=280)
    dpg.add_progress_bar(default_value=0.62, width=420)
    dpg.add_spacer(height=8)
    with dpg.group(horizontal=True):
        for text, kind in (("Save", "fill"), ("Preview", None), ("Reset", "line"), ("Cancel", "ghost")):
            dpg.add_button(label=up(text))
            if kind:
                dpg.bind_item_theme(dpg.last_item(), t[kind])
    dpg.add_spacer(height=8)
    with dpg.table(header_row=True, borders_innerH=True, borders_outerH=True, borders_outerV=True, width=420):
        for h in ("File", "Size", "When"):
            dpg.add_table_column(label=up(h))
        for row in (("colors.lua", "4.1K", "14:02"), ("mono.css", "18K", "13:40"), ("kitty.conf", "1.2K", "yesterday")):
            with dpg.table_row():
                for cell in row:
                    dpg.add_text(cell)

dpg.create_viewport(title=f"mono-ui · dear pygui · {variant}", width=720, height=520, x_pos=0, y_pos=0)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main", True)
dpg.start_dearpygui()
dpg.destroy_context()
