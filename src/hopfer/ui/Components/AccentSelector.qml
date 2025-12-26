import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Material

RowLayout {
    id: root
    spacing: 12

    signal accentSelected(int index)
    property string label: "Accent Color"

    property var colorList: [
        (Material.theme === Material.Light ? "#393d47" : "#f8f8ff"),
        "salmon",
        Material.color(Material.Pink),
        Material.color(Material.Green),
        Material.color(Material.Teal)
    ]
    property int selectedIndex: 0 // Default to the first color

    Label {
        text: root.label
        Layout.fillWidth: true
        color: Material.foreground
    }

    Row {
        spacing: 12 // A bit more space for the rings

        Repeater {
            model: root.colorList

            delegate: Rectangle {
                id: colorCircle
                width: 20
                height: 20
                radius: 10
                color: modelData // Still use the hex for the color

                // The "Ring" logic using index
                Rectangle {
                    id: ring
                    anchors.fill: parent
                    anchors.margins: -5
                    radius: width / 2
                    color: "transparent"
                    border.color: colorCircle.color
                    border.width: 2

                    // Stay visible if this index is selected OR mouse is hovering
                    opacity: {
                        if (mouseArea.containsMouse) {
                            return 0.5;
                        }else if (root.selectedIndex === index) {
                            return 1.0;          // Full visibility if selected
                        } else {
                            return 0.0;          // Hidden otherwise
                        }
                    }

                    Behavior on opacity { NumberAnimation { duration: 150 } }
                }

                MouseArea {
                    id: mouseArea
                    anchors.fill: parent
                    hoverEnabled: true
                    cursorShape: Qt.PointingHandCursor
                    onClicked: {
                        root.selectedIndex = index // Update by index
                        root.accentSelected(index)
                    }
                }
            }
        }
    }
}
