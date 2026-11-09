"""QML (Qt Quick, Quickshell): a `Mono` singleton with every token for every variant.

    import "path/to/dist/qml/MonoUI"       // or add the folder to QML_IMPORT_PATH and: import MonoUI
    Rectangle { color: Mono.bg; radius: Mono.radiusMd; border.color: Mono.line }
    Mono.variant = "square"                 // switches everything bound to it

Also includes MonoButton.qml, MonoLabel.qml, MonoCard.qml as small ready-made components.
"""
from __future__ import annotations

from pathlib import Path

from tokens import HEADER, Tokens, write


def build(t: Tokens, out: Path) -> list[Path]:
    o = out / "qml" / "MonoUI"
    vs = t.variants
    D = [t.v(v) for v in vs]
    R = [t.roles(v) for v in vs]

    def qcolor(c) -> str:
        return f"\"{c.argb8 if not c.opaque else c.hex}\""  # QML reads 8-digit hex as #AARRGGBB

    def pick(vals) -> str:
        vals = list(vals)
        if all(x == vals[0] for x in vals):
            return vals[0]
        return "[" + ", ".join(vals) + "][_i]"

    lit = lambda x: str(x).lower() if isinstance(x, bool) else (f"\"{x}\"" if isinstance(x, str) else str(x))
    props = []
    for k in R[0]:
        props.append(f"    readonly property color {k}: {pick(qcolor(r[k]) for r in R)}")
    for k in D[0]["font"]:
        props.append(f"    readonly property string font{k.capitalize()}: {pick(lit(d['font'][k]['family']) for d in D)}")
    props.append(f"    readonly property int weightDisplay: {pick(lit(d['font']['display']['weight']) for d in D)}")
    props.append(f"    readonly property int weightStrong: {pick(lit(d['font']['strong']['weight']) for d in D)}")
    for k in D[0]["size"]:
        props.append(f"    readonly property int size{k.capitalize()}: {pick(lit(d['size'][k]) for d in D)}")
    for k in D[0]["radius"]:
        props.append(f"    readonly property int radius{k.capitalize()}: {pick(lit(d['radius'][k]) for d in D)}")
    for name, sec, key, typ in (("borderWidth", "border", "width", "int"), ("borderFocus", "border", "focus", "int"),
                                ("controlHeight", "control", "height", "int"), ("controlHeightSmall", "control", "heightSmall", "int"),
                                ("controlPadX", "control", "padX", "int"), ("labelUppercase", "label", "uppercase", "bool"),
                                ("labelTracking", "label", "tracking", "real"), ("labelWeight", "label", "weight", "int")):
        props.append(f"    readonly property {typ} {name}: {pick(lit(d[sec][key]) for d in D)}")
    props.append(f"    readonly property bool isLight: {pick(lit(t.light(v)) for v in vs)}")
    m = t.data["motion"]
    props.append(f"    readonly property int durationFast: {m['fast']}")
    props.append(f"    readonly property int durationBase: {m['base']}")
    for k, x in t.data["space"].items():
        props.append(f"    readonly property int space{k}: {x}")

    mono = f"""// {HEADER}
pragma Singleton
import QtQuick

QtObject {{
    /// {", ".join(f'"{v}"' for v in vs)}. Everything below follows it.
    property string variant: "round"
    readonly property var variants: [{", ".join(f'"{v}"' for v in vs)}]
    readonly property int _i: Math.max(0, variants.indexOf(variant))
    readonly property bool isSquare: radiusMd === 0

{chr(10).join(props)}
}}
"""
    files = []
    p = o / "Mono.qml"
    write(p, mono)
    files.append(p)

    write(o / "qmldir", "module MonoUI\nsingleton Mono 1.0 Mono.qml\nMonoButton 1.0 MonoButton.qml\nMonoLabel 1.0 MonoLabel.qml\nMonoCard 1.0 MonoCard.qml\n")
    files.append(o / "qmldir")

    write(o / "MonoLabel.qml", f"""// {HEADER}
import QtQuick

/// Text in one of the mono roles: "body", "label", "h1", "h2", "h3", "muted", "faint", "mono", "stat".
Text {{
    property string role: "body"
    readonly property bool isLabel: role === "label"
    color: role === "h1" || role === "h2" || role === "h3" || role === "stat" ? Mono.fg
         : role === "label" || role === "muted" ? Mono.fgMuted
         : role === "faint" ? Mono.fgFaint : Mono.fgDim
    font.family: role === "h1" || role === "h2" || role === "stat" ? Mono.fontDisplay
               : role === "h3" || role === "label" ? Mono.fontStrong
               : role === "mono" ? Mono.fontMono : Mono.fontSans
    font.weight: role === "h1" || role === "h2" || role === "stat" ? Mono.weightDisplay
               : role === "h3" ? Mono.weightStrong : role === "label" ? Mono.labelWeight : Font.Normal
    readonly property int px: role === "h1" ? Math.min(Mono.sizeH2, 48)
                            : role === "h2" ? Math.round((Math.min(Mono.sizeH2, 48) + Mono.sizeH3) / 2)
                            : role === "h3" ? Mono.sizeH3 : role === "label" ? Mono.sizeLabel
                            : role === "stat" ? Mono.sizeStat : role === "mono" ? Mono.sizeSmall : Mono.sizeUi
    font.pixelSize: px
    font.capitalization: isLabel && Mono.labelUppercase ? Font.AllUppercase : Font.MixedCase
    font.letterSpacing: isLabel ? Mono.labelTracking * px : 0
}}
""")
    write(o / "MonoButton.qml", f"""// {HEADER}
import QtQuick

/// kind: "outline" (default), "fill", "line", "ghost"
Rectangle {{
    id: root
    property string text: ""
    property string kind: "outline"
    signal clicked()

    readonly property bool hovered: area.containsMouse
    implicitHeight: Mono.controlHeight
    implicitWidth: label.implicitWidth + Mono.controlPadX * 2
    radius: Mono.radiusMd
    opacity: enabled ? 1 : 0.45
    color: kind === "fill" ? (hovered ? Mono.accentHover : Mono.accent)
         : hovered ? Mono.tint : "transparent"
    border.width: Mono.borderWidth
    border.color: kind === "fill" ? color
                : kind === "ghost" ? "transparent"
                : kind === "line" && !hovered ? Mono.lineStrong : Mono.fg
    Behavior on color {{ ColorAnimation {{ duration: Mono.durationFast }} }}

    MonoLabel {{
        id: label
        anchors.centerIn: parent
        text: root.text
        role: "label"
        color: root.kind === "fill" ? Mono.onAccent : root.kind === "ghost" && !root.hovered ? Mono.fgMuted : Mono.fg
    }}
    MouseArea {{
        id: area
        anchors.fill: parent
        hoverEnabled: true
        enabled: root.enabled
        cursorShape: Qt.PointingHandCursor
        onClicked: root.clicked()
    }}
}}
""")
    write(o / "MonoCard.qml", f"""// {HEADER}
import QtQuick

Rectangle {{
    default property alias content: inner.data
    property int padding: 16
    color: Mono.surface
    radius: Mono.radiusLg
    border.width: Mono.borderWidth
    border.color: Mono.line
    implicitWidth: inner.childrenRect.width + padding * 2
    implicitHeight: inner.childrenRect.height + padding * 2
    Item {{ id: inner; anchors.fill: parent; anchors.margins: parent.padding }}
}}
""")
    files += [o / "MonoLabel.qml", o / "MonoButton.qml", o / "MonoCard.qml"]
    return files
