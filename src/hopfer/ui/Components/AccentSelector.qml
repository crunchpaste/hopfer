import QtQuick
import QtQuick.Layouts
import QtQuick.Controls.Material

RowLayout {
    id: root
    spacing: 12

    signal accentSelected(int index)
    property string label: "Accent Color"

    property var colorList: [
        (Material.theme === Material.Dark ? "#f8f8ff" : "#393d47"),
        (Material.theme === Material.Dark ? "#fa8072" : "#e95044"),
        (Material.theme === Material.Dark ? "#f48fb1" : "#e91e63"),
        (Material.theme === Material.Dark ? "#a5d6a7" : "#4caf50"),
        (Material.theme === Material.Dark ? "#80cbc4" : "#009688"),
    ]
    property int selectedIndex: 0

    Label {
        text: root.label
        Layout.fillWidth: true
        color: Material.foreground
    }

    Row {
        spacing: 12

        Repeater {
            model: root.colorList

            delegate: Rectangle {
                id: colorCircle
                width: 20
                height: 20
                radius: 10
                color: modelData

                Rectangle {
                    id: ring
                    anchors.fill: parent
                    anchors.margins: -5
                    radius: width / 2
                    color: "transparent"
                    border.color: colorCircle.color
                    border.width: 2

                    opacity: {
                        if (mouseArea.containsMouse) {
                            return 0.5;
                        }else if (root.selectedIndex === index) {
                            return 1.0;
                        } else {
                            return 0.0;
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
                        root.selectedIndex = index
                        root.accentSelected(index)
                    }
                }
            }
        }
    }
}
