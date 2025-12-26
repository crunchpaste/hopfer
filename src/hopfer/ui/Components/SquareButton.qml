import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material

Item {
    id: root

    property var icon
    property color color: mouse.hovered ? Material.accent : Material.foreground

    signal clicked()

    ToolTip.visible: mouse.hovered
    ToolTip.text: ""
    ToolTip.delay: 1000 // Optional: Wait 500ms before showing
    width: 40
    height: 40
    opacity: enabled ? 1 : 0.3

    Rectangle {
        id: hoverBg

        anchors.fill: parent
        radius: 5
        color: Qt.alpha(Material.foreground, 0)
        states: [
            State {
                name: "hovered"
                when: mouse.hovered

                PropertyChanges {
                    target: hoverBg
                    color: Qt.alpha(Material.foreground, 0.3)
                }

            }
        ]
        transitions: [
            Transition {
                to: "hovered"

                ColorAnimation {
                    duration: 50
                }

            },
            Transition {
                from: "hovered"

                ColorAnimation {
                    duration: 1500
                    easing.type: Easing.OutCubic
                }

            }
        ]
    }

    Loader {
        id: iconLoader

        anchors.centerIn: parent
        width: parent.width * .55
        height: parent.height * .55
        sourceComponent: root.icon
        onLoaded: {
            // Check if the loaded item has a 'fill' or 'color' property
            // We bind the loaded item's color to our root.iconColor
            if (item.hasOwnProperty("fill")) {
                item.fill = Qt.binding(() => root.color)
            }
        }
    }

    HoverHandler {
        id: mouse

        acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
        cursorShape: Qt.PointingHandCursor
        enabled: root.enabled
    }

    TapHandler {
        enabled: root.enabled
        onTapped: {
            root.clicked();
        }
    }

}
