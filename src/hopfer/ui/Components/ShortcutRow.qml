import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

RowLayout {
    id: root
    property alias label: action.text
    property string sequence: "Ctrl+Shift+V"
    spacing: 8
    Label {
        id: action
    }
    Item {
        Layout.fillWidth: true
    }
    Repeater {
        model: sequence.split("+")

        delegate: Rectangle {
            id: keyCap
            color: Qt.alpha(Material.foreground, 0.075)
            radius: 3

            implicitHeight: key.implicitHeight + 12
            implicitWidth: Math.max(implicitHeight, key.implicitWidth + 18)

            Label {
                id: key
                anchors.centerIn: parent
                text: modelData
            }
        }
    }
}
