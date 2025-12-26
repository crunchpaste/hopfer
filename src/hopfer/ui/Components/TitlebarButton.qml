import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material

Item {
    id: root

    property var icon
    property color color: mouse.hovered ? Material.accent : Material.foreground

    signal clicked()

    width: 30
    height: 30
    opacity: enabled ? 1 : 0.3

    Rectangle {
        id: hoverBg

        anchors.fill: parent
        radius: 15
        color: Qt.alpha(Material.foreground, 0)
        states: [
            State {
                name: "hovered"
                when: mouse.hovered

                PropertyChanges {
                    target: hoverBg
                    color: Qt.alpha(Material.foreground, 0.2)
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
        width: parent.width * .8
        height: parent.height * .8
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
        gesturePolicy: TapHandler.WithinBounds
        onTapped: {
            root.clicked();
        }
    }

}
