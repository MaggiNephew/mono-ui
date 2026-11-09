#!/usr/bin/env python3
"""mono-ui Textual demo.

    python3 demo.py            round
    python3 demo.py square
    python3 demo.py round --shot out.svg     save a screenshot and exit
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "dist" / "textual"))
from mono_textual import MonoApp  # noqa: E402

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (Button, Checkbox, DataTable, Footer, Input, ListItem, ListView, Label,
                             ProgressBar, RadioButton, RadioSet, Static, Switch, TabbedContent, TabPane)


class Demo(MonoApp):
    TITLE = "mono-ui · Textual"
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="side"):
                yield Label("Workspaces", classes="label")
                yield ListView(*(ListItem(Label(n)) for n in ["Black Hole", "Event Horizon", "Predator", "cyber"]), id="list")
                yield Label("textual · tokens/mono.json", classes="faint")
            with Vertical(id="main"):
                yield Label("05 · Terminal", classes="label")
                yield Label("cyber", classes="h1")
                yield Label("BlackArch tool browser · firejail sandbox · online / offline", classes="muted")
                with Horizontal(classes="stats"):
                    for value, name in (("2847", "Tools"), ("51", "Categories"), ("12", "Favourites"), ("off", "Network")):
                        with Vertical(classes="cell"):
                            yield Static(value, classes="value")
                            yield Label(name, classes="label")
                with Horizontal(id="buttons"):
                    yield Button("Launch", classes="-fill")
                    yield Button("Sandbox", classes="-line")
                    yield Button("Outline")
                    yield Button("Ghost", classes="-ghost")
                    yield Button("Disabled", disabled=True)
                with TabbedContent():
                    with TabPane("Settings"):
                        yield Input(placeholder="Search tools…")
                        with Horizontal(id="checks"):
                            yield Checkbox("Sandbox", True)
                            yield Checkbox("Mouse")
                            yield Switch(value=True)
                            with RadioSet():
                                yield RadioButton("Offline", True)
                                yield RadioButton("Online")
                        yield ProgressBar(total=100, show_eta=False, id="bar")
                    with TabPane("Tools"):
                        yield DataTable(id="table")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#bar", ProgressBar).progress = 64
        t = self.query_one("#table", DataTable)
        t.add_columns("Tool", "Category", "Sandbox")
        t.add_rows([("nmap", "scanner", "offline"), ("wireshark", "sniffer", "offline"), ("ghidra", "reversing", "offline")])

    CSS = """
#side { width: 30; padding: 1 1; border-right: solid $mono-line; }
#list { height: 1fr; margin: 1 0; }
#main { padding: 1 2; }
#buttons { height: auto; margin: 1 0; }
#buttons Button { margin-right: 1; }
#checks { height: auto; margin: 1 0; }
#checks > * { margin-right: 2; }
RadioSet { layout: horizontal; border: none; background: transparent; }
.stats { margin-top: 1; }
"""


if __name__ == "__main__":
    args = sys.argv[1:]
    variant = next((a for a in args if a in ("square", "round", "blend", "paper")), "round")
    app = Demo(variant=variant)
    if "--shot" in args:
        out = args[args.index("--shot") + 1]

        async def shoot():
            async with app.run_test(size=(120, 36)) as pilot:
                await pilot.pause(0.3)
                Path(out).write_text(app.export_screenshot())
        import asyncio
        asyncio.run(shoot())
    else:
        app.run()
