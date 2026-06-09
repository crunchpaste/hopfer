import Icons
import QtCore
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ColumnLayout {
    // Layout.topMargin: -12

    id: root

    property alias text: label.text
    property alias valueText: valueDisplay.text
    property alias from: slider.from
    property alias to: slider.to
    property alias step: slider.stepSize
    property alias value: slider.value
    property alias snapMode: slider.snapMode
    property real default_value: 0
    property int precision: 0

    signal interaction(real value)
    signal moved()
    signal valueChange()

    RowLayout {
        Layout.bottomMargin: -20
        z: 10

        Label {
            id: label

            text: "Local threshold"
            font.family: "Jetbrains Mono"
            // font.pointSize: 11
        }

        Item {
            width: 26
            height: 26
            z: 10
            // visible: slider.value !== root.default_value
            // Layout.hideOnInvisible: false
            // working with visible made the layout shift a bit and it was annoying
            opacity: slider.value.toFixed(root.precision) != root.default_value.toFixed(root.precision) ? 1 : 0

            Rectangle {
                id: hoverBg

                anchors.fill: parent
                radius: width / 2
                color: "transparent"
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

            Restore {
                anchors.centerIn: parent
                width: 18
                height: 18
                fill: mouse.hovered ? Material.accent : Material.foreground
            }

            HoverHandler {
                id: mouse

                acceptedDevices: PointerDevice.Mouse | PointerDevice.TouchPad
                cursorShape: Qt.PointingHandCursor
                enabled: slider.value.toFixed(root.precision) != root.default_value.toFixed(root.precision)
            }

            TapHandler {
                enabled: slider.value.toFixed(root.precision) != root.default_value.toFixed(root.precision)
                onTapped: {
                    slider.value = root.default_value;
                    root.interaction(root.value);

                }
            }

        }

        Item {
            Layout.fillWidth: true
        }

        Label {
            id: valueDisplay

            text: slider.value.toFixed(root.precision) ** 2
            font.family: "Jetbrains Mono"
            // font.pointSize: 11
        }

    }

    Slider {
        id: slider

        from: 0
        to: 1
        stepSize: 0.01
        value: 1
        Layout.leftMargin: -13
        Layout.rightMargin: -13
        Layout.fillWidth: true
        onPressedChanged: {
            if (!pressed)
                root.interaction(root.value);
        }
        onMoved: {
          root.moved()
        }

    }

}
