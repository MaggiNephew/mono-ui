// mono-ui QML demo:  QML_IMPORT_PATH=../../dist/qml qml main.qml
// (or run demo.py, which does the same through PySide6)
import QtQuick
import QtQuick.Window
import MonoUI

Window {
    id: win
    width: 900
    height: 460
    visible: true
    color: Mono.bg
    title: "mono-ui · QML"

    Column {
        anchors.fill: parent
        anchors.margins: 28
        spacing: 14

        Row {
            spacing: 10
            MonoLabel { role: "label"; text: "06 · Qt Quick"; anchors.verticalCenter: parent.verticalCenter }
            MonoButton { text: Mono.variant; kind: "line"; implicitHeight: Mono.controlHeightSmall
                onClicked: Mono.variant = Mono.variants[(Mono.variants.indexOf(Mono.variant) + 1) % Mono.variants.length] }
        }
        MonoLabel { role: "h1"; text: "Orbital lock" }
        MonoLabel { role: "muted"; text: "the same animated lock for boot (SDDM) and Super+L (Quickshell)" }

        // stats strip
        Rectangle {
            width: parent.width; height: 74
            color: "transparent"; radius: Mono.radiusMd
            border.width: Mono.borderWidth; border.color: Mono.line
            Row {
                anchors.fill: parent
                Repeater {
                    model: [["02:14", "Uptime"], ["3", "Monitors"], ["on", "Blur"], ["120", "FPS"]]
                    Item {
                        width: parent.width / 4; height: parent.height
                        Rectangle { visible: index > 0; width: 1; height: parent.height; color: Mono.line }
                        Column {
                            anchors.left: parent.left; anchors.leftMargin: 14; anchors.verticalCenter: parent.verticalCenter; spacing: 2
                            MonoLabel { role: "stat"; text: modelData[0] }
                            MonoLabel { role: "label"; text: modelData[1] }
                        }
                    }
                }
            }
        }

        Row {
            spacing: 8
            MonoButton { text: "Lock now"; kind: "fill" }
            MonoButton { text: "Preview SDDM"; kind: "line" }
            MonoButton { text: "Outline" }
            MonoButton { text: "Ghost"; kind: "ghost" }
            MonoButton { text: "Disabled"; enabled: false }
        }

        MonoCard {
            width: parent.width
            Column {
                spacing: 4
                MonoLabel { role: "h3"; text: "Black hole shader" }
                MonoLabel { role: "muted"; text: "blackhole.frag · Orbital.qml · qylock" }
                MonoLabel { role: "mono"; text: "config/quickshell/lock/shaders/blackhole.frag.qsb" }
            }
        }
    }
}
