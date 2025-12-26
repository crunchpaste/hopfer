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

    width: Math.min(parent.width * 0.8, 400)
    height: 60
    radius: 4
    color: Qt.darker(Material.background, 1.1)
    anchors.horizontalCenter: parent.horizontalCenter
    anchors.bottom: parent.bottom
    anchors.bottomMargin: 46
    opacity: visibleSnackbar ? 1 : 0

    Timer {
        id: timer

        interval: root.duration
        repeat: false
        onTriggered: root.hide()
    }

    RowLayout {
        anchors.fill: parent

        Text {
            id: label

            Layout.leftMargin: 24
            text: ""
            color: Material.foreground
            font.pointSize: 11
        }

        Item {
            Layout.fillWidth: true
            Layout.minimumWidth: 24
        }

        RoundButton {
            text: "Ok"
            // font.weight: font.SemiBold
            Layout.rightMargin: 12
            Material.background: root.color
            // color: Material.accentColor
            onClicked: root.hide()
            Material.elevation: 0
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
