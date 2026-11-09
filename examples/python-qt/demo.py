#!/usr/bin/env python3
"""mono-ui Qt demo (PySide6 or PyQt6).

    python3 demo.py            round variant
    python3 demo.py square     square variant
    python3 demo.py round --shot out.png   save a screenshot and exit
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "dist" / "qt" / "python"))
from mono_qt import apply, kind, role  # noqa: E402

try:
    from PySide6.QtCore import Qt, QTimer
    from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel,
                                   QLineEdit, QListWidget, QMainWindow, QProgressBar, QPushButton, QRadioButton,
                                   QSlider, QSpinBox, QTableWidget, QTableWidgetItem, QTabWidget, QTextEdit,
                                   QVBoxLayout, QWidget, QAbstractItemView, QHeaderView)
except ImportError:
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel,
                                 QLineEdit, QListWidget, QMainWindow, QProgressBar, QPushButton, QRadioButton,
                                 QSlider, QSpinBox, QTableWidget, QTableWidgetItem, QTabWidget, QTextEdit,
                                 QVBoxLayout, QWidget, QAbstractItemView, QHeaderView)


def stats(pairs):
    box = role(QFrame(), "stats")
    lay = QHBoxLayout(box)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(0)
    for i, (num, name) in enumerate(pairs):
        cell = QFrame()
        if i < len(pairs) - 1:
            role(cell, "cell")
        v = QVBoxLayout(cell)
        v.setContentsMargins(14, 12, 14, 10)
        v.setSpacing(2)
        v.addWidget(role(QLabel(num), "stat"))
        v.addWidget(role(QLabel(name), "label"))
        lay.addWidget(cell)
    return box


def build(variant: str) -> QMainWindow:
    win = QMainWindow()
    win.setWindowTitle(f"mono-ui · Qt · {variant}")
    root = QWidget()
    win.setCentralWidget(root)
    outer = QHBoxLayout(root)
    outer.setContentsMargins(0, 0, 0, 0)
    outer.setSpacing(0)

    # sidebar
    side = QWidget()
    side.setFixedWidth(200)
    sv = QVBoxLayout(side)
    sv.setContentsMargins(16, 18, 12, 16)
    sv.addWidget(role(QLabel("Workspaces"), "label"))
    lst = QListWidget()
    lst.addItems(["Black Hole", "Event Horizon", "Predator", "Stream kit", "Soundboard"])
    lst.setCurrentRow(0)
    sv.addWidget(lst, 1)
    sv.addWidget(role(QLabel("v1.0 · tokens/mono.json"), "mono"))
    outer.addWidget(side)
    rule = role(QFrame(), "rule")
    rule.setFixedWidth(1)
    rule.setMaximumHeight(16777215)
    outer.addWidget(rule)

    # main
    main = QWidget()
    mv = QVBoxLayout(main)
    mv.setContentsMargins(28, 22, 28, 22)
    mv.setSpacing(14)
    mv.addWidget(role(QLabel("01 · Settings"), "label"))
    mv.addWidget(role(QLabel("Black Hole"), "h1"))
    mv.addWidget(role(QLabel("Proxmox VE 9.2 · Ryzen 9 7900X · RTX 3060"), "muted"))
    mv.addWidget(stats([("24", "Threads"), ("64", "GB memory"), ("2", "TB NVMe"), ("1", "TB backup")]))

    buttons = QHBoxLayout()
    buttons.setSpacing(8)
    buttons.addWidget(kind(QPushButton("Open console"), "fill"))
    buttons.addWidget(kind(QPushButton("Mirror report"), "line"))
    buttons.addWidget(QPushButton("Outline"))
    buttons.addWidget(kind(QPushButton("Ghost"), "ghost"))
    off = QPushButton("Disabled")
    off.setEnabled(False)
    buttons.addWidget(off)
    buttons.addStretch(1)
    mv.addLayout(buttons)

    tabs = QTabWidget()
    # form tab
    form = QWidget()
    g = QGridLayout(form)
    g.setContentsMargins(16, 16, 16, 16)
    g.setHorizontalSpacing(18)
    g.setVerticalSpacing(10)
    g.addWidget(role(QLabel("Hostname"), "label"), 0, 0)
    g.addWidget(QLineEdit("black-hole"), 1, 0)
    g.addWidget(role(QLabel("Variant"), "label"), 0, 1)
    combo = QComboBox()
    combo.addItems(["square", "round", "blend", "paper"])
    combo.setCurrentText(variant)
    g.addWidget(combo, 1, 1)
    g.addWidget(role(QLabel("Snapshots kept"), "label"), 0, 2)
    spin = QSpinBox()
    spin.setValue(7)
    g.addWidget(spin, 1, 2)
    search = QLineEdit()
    search.setPlaceholderText("Search packages…")
    g.addWidget(search, 2, 0, 1, 2)
    checks = QHBoxLayout()
    checks.setSpacing(22)
    c1 = QCheckBox("Nightly backup")
    c1.setChecked(True)
    checks.addWidget(c1)
    checks.addWidget(QCheckBox("Offline"))
    r1 = QRadioButton("Apt mirror")
    r1.setChecked(True)
    checks.addWidget(r1)
    checks.addWidget(QRadioButton("Direct"))
    checks.addStretch(1)
    g.addLayout(checks, 3, 0, 1, 3)
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setValue(62)
    g.addWidget(slider, 4, 0, 1, 2)
    bar = QProgressBar()
    bar.setValue(64)
    g.addWidget(bar, 4, 2)
    notes = QTextEdit("Backups run at 02:30 and go to Event Horizon.\n7 daily · 4 weekly · 3 monthly.")
    notes.setFixedHeight(70)
    g.addWidget(notes, 5, 0, 1, 3)
    g.setRowStretch(6, 1)
    tabs.addTab(form, "Settings")

    # table tab
    table = QTableWidget(4, 3)
    table.setHorizontalHeaderLabels(["Machine", "Address", "Role"])
    rows = [("Black Hole", "10.10.10.10", "Proxmox server"), ("Event Horizon", "10.10.10.11", "Backups + apt mirror"),
            ("Predator", "10.10.10.20", "Laptop · Hyprland"), ("Pi", "10.10.10.12", "DNS")]
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            table.setItem(r, c, QTableWidgetItem(val))
    table.verticalHeader().setVisible(False)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.selectRow(1)
    tabs.addTab(table, "Machines")
    tabs.addTab(QWidget(), "Logs")
    mv.addWidget(tabs, 1)

    card = role(QFrame(), "card")
    cl = QHBoxLayout(card)
    cl.setContentsMargins(16, 12, 12, 12)
    tv = QVBoxLayout()
    tv.addWidget(role(QLabel("Next backup"), "h3"))
    tv.addWidget(role(QLabel("Tonight 02:30 → Event Horizon"), "muted"))
    cl.addLayout(tv, 1)
    cl.addWidget(kind(QPushButton("Run now"), "fill"))
    mv.addWidget(card)

    outer.addWidget(main, 1)
    win.resize(980, 720)
    win.statusBar().showMessage("10.10.10.0/24 · offline · 3 machines")
    return win


def main():
    args = sys.argv[1:]
    variant = next((a for a in args if a in ("square", "round", "blend", "paper")), "round")
    shot = args[args.index("--shot") + 1] if "--shot" in args else None
    app = QApplication(sys.argv[:1])
    apply(app, variant)
    win = build(variant)
    win.show()
    if shot:
        QTimer.singleShot(300, lambda: (win.grab().save(shot), app.quit()))
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
