#!/usr/bin/env python3
"""Run main.qml with PySide6.   python3 demo.py [square|round] [--shot out.png]"""
import sys
from pathlib import Path

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from shiboken6 import Shiboken

root = Path(__file__).resolve().parents[2]
args = sys.argv[1:]
variant = next((a for a in args if a in ("square", "round", "blend", "paper")), "round")

app = QGuiApplication(sys.argv[:1])
for f in (root / "fonts" / "ttf").glob("*.ttf"):
    QFontDatabase.addApplicationFont(str(f))
engine = QQmlApplicationEngine()
engine.addImportPath(str(root / "dist" / "qml"))
engine.load(QUrl.fromLocalFile(str(Path(__file__).with_name("main.qml"))))
if not engine.rootObjects():
    sys.exit(1)
win = engine.rootObjects()[0]
if not isinstance(win, QQuickWindow):  # PySide hands back the base QWindow wrapper
    win = Shiboken.wrapInstance(Shiboken.getCppPointer(win)[0], QQuickWindow)
mono = engine.singletonInstance("MonoUI", "Mono")
mono.setProperty("variant", variant)

if "--shot" in args:
    out = args[args.index("--shot") + 1]

    def shot():
        try:
            win.grabWindow().save(out)
        finally:
            app.quit()
    QTimer.singleShot(500, shot)
sys.exit(app.exec())
