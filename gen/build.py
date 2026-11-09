#!/usr/bin/env python3
"""Build every mono-ui target from tokens/mono.json.

    python3 gen/build.py            build everything into dist/
    python3 gen/build.py web qt     build only some targets
    python3 gen/build.py --list     show targets

No dependencies beyond Python 3.10+.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "targets"))

from tokens import ROOT, Tokens  # noqa: E402

TARGETS = ["exports", "web", "qt", "imgui", "gtk", "textual", "qml", "editors", "terminals", "webext", "desktop", "apps", "rice"]


def main(argv: list[str]) -> int:
    if "--list" in argv:
        print("\n".join(TARGETS))
        return 0
    wanted = [a for a in argv if not a.startswith("-")] or TARGETS
    unknown = set(wanted) - set(TARGETS)
    if unknown:
        print(f"unknown target(s): {', '.join(sorted(unknown))}. Try --list.", file=sys.stderr)
        return 2

    t = Tokens()
    out = ROOT / "dist"
    out.mkdir(exist_ok=True)
    total = 0
    for name in wanted:
        target_dir = out / name
        before = {p for p in target_dir.rglob("*") if p.is_file()} if target_dir.exists() else set()
        mod = importlib.import_module(name)
        files = mod.build(t, out)  # overwrites in place
        total += len(files)
        stale = before - {Path(f) for f in files}
        for p in stale:  # files a previous build made that this one didn't
            try:
                p.unlink()
            except OSError:
                print(f"  (couldn't remove stale {p.relative_to(ROOT)})", file=sys.stderr)
        print(f"  {name:<8} {len(files):>3} files" + (f", removed {len(stale)} stale" if stale else ""))
    print(f"done: {total} files in {out.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
