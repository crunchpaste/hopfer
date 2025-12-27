import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

Rectangle {
    id: root

    property alias text: label.text
    property int duration: 5000 // milliseconds
    property bool visibleSnackbar: false

    function show(message, duration) {
        text = message;
        timer.interval = duration;
        visibleSnackbar = true;
        timer.restart();
    }

    function hide() {
        visibleSnackbar = false;
        timer.stop();
    }

    width: Math.min(parent.width * 0.8, 500)
    height: row.implicitHeight + 20

    radius: 4
    color: Qt.darker(Material.background, 1.2)
    anchors.horizontalCenter: parent.horizontalCenter
    opacity: visibleSnackbar ? 1 : 0

    Timer {
        id: timer

        interval: root.duration
        repeat: false
        onTriggered: root.hide()
    }

    RowLayout {
        id: row
        anchors.fill: parent

        Text {
            id: label

            Layout.fillWidth: true
            Layout.leftMargin: 24
            text: ""
            color: Material.foreground
            font.family: "Jetbrains Mono"
            font.pointSize: 11
            wrapMode: Text.Wrap
        }

        Item {
            width: 24
        }

        RoundButton {
            id: ok
            text: "Ok"
            font.family: "Jetbrains Mono"
            font.pointSize: 11
            Layout.rightMargin: 12
            Material.background: root.color
            // text.color: Material.accent
            flat: true
            onClicked: root.hide()
            Material.elevation: 0

            // just so that it appears with the accent color.
            contentItem: Text {
                    text: ok.text
                    font: ok.font
                    opacity: enabled ? 1.0 : 0.3
                    color: ok.down ? Material.foreground : Material.accent
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
        }

    }

    Behavior on opacity {
        NumberAnimation {
            duration: 100
        }

    }

    HoverHandler {
        id: mouse
        acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
        onHoveredChanged: {
            if (hovered) {
                timer.restart()
                timer.stop()
            } else {
                timer.start()
            }
        }
    }
}
