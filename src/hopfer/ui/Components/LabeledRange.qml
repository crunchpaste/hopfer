import Icons
import QtCore
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ColumnLayout {
    id: root

    property alias text: label.text
    property alias from: slider.from
    property alias to: slider.to
    property alias step: slider.stepSize
    property var value: [slider.first.value, slider.second.value]
    property alias value0: slider.first.value
    property alias value1: slider.second.value
    property int precision: 2
    property var default_values: [0.0, 1.0]

    signal interaction()

    function update_values() {
        let new_values = [slider.first.value, slider.second.value];
        root.value = new_values;
    }

    RowLayout {
        Layout.bottomMargin: -20
        z: 10

        Label {
            id: label

            text: "Local threshold"
            font.family: "Jetbrains Mono"
            font.pointSize: 11
        }

        Item {
            width: 26
            height: 26
            z: 10
            // visible: slider.value !== root.default_value
            // Layout.hideOnInvisible: false
            // working with visible made the layout shift a bit and it was annoying
            // Slightly overkill but still, better than glitching
            opacity: (slider.first.value.toFixed(root.precision) != root.default_values[0].toFixed(root.precision) || slider.second.value.toFixed(root.precision) != root.default_values[1].toFixed(root.precision)) ? 1 : 0

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
                enabled: (slider.first.value.toFixed(root.precision) != root.default_values[0].toFixed(root.precision) || slider.second.value.toFixed(root.precision) != root.default_values[1].toFixed(root.precision))
            }

            TapHandler {
                enabled: (slider.first.value.toFixed(root.precision) != root.default_values[0].toFixed(root.precision) || slider.second.value.toFixed(root.precision) != root.default_values[1].toFixed(root.precision))
                onTapped: {
                    slider.first.value = root.default_values[0];
                    slider.second.value = root.default_values[1];
                    root.interaction();
                }
            }

        }

        Item {
            Layout.fillWidth: true
        }

        Label {
            id: valueDisplay

            text: slider.first.value.toFixed(root.precision) + " → " + slider.second.value.toFixed(root.precision)
            font.family: "Jetbrains Mono"
            font.pointSize: 11
        }

    }

    RangeSlider {
        id: slider

        Material.roundedScale: Material.SmallScale
        from: 0
        to: 1
        stepSize: 0.01
        first.value: 0
        second.value: 1
        Layout.leftMargin: -13
        Layout.rightMargin: -13
        Layout.fillWidth: true
        first.onValueChanged: {
            root.update_values();
        }
        second.onValueChanged: {
            root.update_values();
        }
        first.onPressedChanged: {
            if (!first.pressed)
                root.interaction();

        }
        second.onPressedChanged: {
            if (!second.pressed)
                root.interaction();

        }
    }

}
