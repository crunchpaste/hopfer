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
    property alias from: slider.from
    property alias to: slider.to
    property alias step: slider.stepSize
    property alias value: slider.value
    property real default_value: 0
    property int precision: 0

    signal interaction()
    signal moved()
    signal valueChange()

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
            Layout.fillWidth: true
        }

        Label {
            id: valueDisplay

            text: slider.value.toFixed(root.precision)
            font.family: "Jetbrains Mono"
            font.pointSize: 11
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
                root.interaction();
        }
        onMoved: {
          root.moved()
        }

    }

}
