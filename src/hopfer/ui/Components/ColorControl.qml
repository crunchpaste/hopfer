import Icons
import QtCore
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

RowLayout {
    id: root
    spacing: 24

    property string _previousValidHex: ""
    property color color: "#ff0000"
    property alias text: label.text

    signal colorSelected(color newColor)
    signal openColorPicker(color color)

    Label {
        id: label
        text: "Print"
    }
    // Item {width: 12}

    TextField {
        id: hexInput
        text: colorToHex(root.color)
        selectByMouse: true
        Layout.fillWidth: true
        horizontalAlignment: TextInput.AlignHCenter
        verticalAlignment: TextInput.AlignVCenter

        background.implicitHeight: 32

        validator: RegularExpressionValidator {
            regularExpression: /^#?[A-Fa-f0-9]{6}$|^#?[A-Fa-f0-9]{3}$/
        }

        onTextEdited: {
            // If the user typed something and forgot the #, add it automatically
            if (text.length > 0 && text[0] !== '#') {
                let cursor = cursorPosition // Save cursor to prevent it jumping to the end
                text = "#" + text
                cursorPosition = cursor + 1
            }
        }

        onActiveFocusChanged: {
            if (activeFocus) {
                // 1. Remember what it was before they started messing with it
                _previousValidHex = text
                selectAll()
            } else {
                // 2. If they click away and the input is invalid, revert!
                if (!acceptableInput) {
                    text = _previousValidHex
                }
            }
        }

        onEditingFinished: {
            if (acceptableInput) {
                let cleanColor = text.startsWith("#") ? text : "#" + text
                if (cleanColor != _previousValidHex) {
                    root.color = cleanColor
                    root.colorSelected(cleanColor)
                }
            }
        }
    }

    // The Button with the Color Swatch
    Rectangle {
        id: swatch
        Layout.preferredHeight: hexInput.height - 4
        Layout.preferredWidth: height
        radius: 4
        color: root.color

        border.width: 2
        border.color: Material.foreground

        // Optional: Add a subtle hover effect
        opacity: mouseArea.containsMouse ? 0.8 : 1.0

        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true

            onClicked: {
                color_picker.startColor = root.color
                color_picker.currentColor = root.color
                color_picker.show()
                color_picker.raise()
            }

            onPressed: {
                swatch.scale = 0.95
            }

            onReleased: {
                swatch.scale = 1.0
            }
        }

        Behavior on color {
            ColorAnimation { duration: 150 }
        }
    }

    ColorPicker {
        id: color_picker
        modality: Qt.WindowModal
        currentColor: root.color
        onColorAccepted: (newColor) => {
            root.color = newColor
            root.colorSelected(newColor)
        }
    }

    function colorToHex(c) {
        return "#" + c.toString().substring(1, 7)
    }
}
