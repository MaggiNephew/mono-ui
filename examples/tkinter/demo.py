"""Tkinter demo: python3 examples/tkinter/demo.py [square|round|blend|paper]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "dist" / "apps" / "tkinter"))
import tkinter as tk
from tkinter import ttk

from mono_tk import apply, label

variant = sys.argv[1] if len(sys.argv) > 1 else "round"
root = tk.Tk()
root.title(f"mono-ui · tkinter · {variant}")
root.geometry("720x480")
apply(root, variant)

f = ttk.Frame(root, padding=24)
f.pack(fill="both", expand=True)
label(f, "01 · Settings", variant=variant).grid(row=0, column=0, columnspan=3, sticky="w")
ttk.Label(f, text="Display", style="H1.TLabel").grid(row=1, column=0, columnspan=3, sticky="w", pady=(2, 12))
ttk.Label(f, text="Changes apply after a restart.", style="Muted.TLabel").grid(row=2, column=0, columnspan=3, sticky="w")

label(f, "Name", variant=variant).grid(row=3, column=0, sticky="w", pady=(16, 4))
e = ttk.Entry(f, width=28); e.insert(0, "mono"); e.grid(row=4, column=0, sticky="we", padx=(0, 12))
label(f, "Theme", variant=variant).grid(row=3, column=1, sticky="w", pady=(16, 4))
c = ttk.Combobox(f, values=["square", "round", "blend", "paper"], state="readonly", width=14); c.set(variant); c.grid(row=4, column=1, sticky="w")

v1, v2 = tk.BooleanVar(value=True), tk.StringVar(value="a")
ttk.Checkbutton(f, text="Show hidden files", variable=v1).grid(row=5, column=0, sticky="w", pady=(16, 0))
ttk.Radiobutton(f, text="Compact", variable=v2, value="a").grid(row=6, column=0, sticky="w", pady=(6, 0))
ttk.Radiobutton(f, text="Comfortable", variable=v2, value="b").grid(row=6, column=1, sticky="w", pady=(6, 0))
pb = ttk.Progressbar(f, value=62, length=300); pb.grid(row=7, column=0, columnspan=2, sticky="we", pady=(18, 0))

b = ttk.Frame(f); b.grid(row=8, column=0, columnspan=3, sticky="w", pady=(22, 0))
ttk.Button(b, text="Save", style="Fill.TButton").pack(side="left", padx=(0, 8))
ttk.Button(b, text="Preview").pack(side="left", padx=(0, 8))
ttk.Button(b, text="Reset", style="Line.TButton").pack(side="left", padx=(0, 8))
ttk.Button(b, text="Cancel", style="Ghost.TButton").pack(side="left")
root.mainloop()
