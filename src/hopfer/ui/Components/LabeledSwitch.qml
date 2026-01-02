import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

RowLayout {
    id: root

    property alias text: label.text
    property alias value: toggle.checked

    signal interaction()

    Label {
        id: label

        text: "Serpentine"
        font.family: "Jetbrains Mono"
        // font.pointSize: 11
    }

    Item {
        Layout.fillWidth: true
    }

    Switch {
        id: toggle

        Layout.rightMargin: -15
        onToggled: root.interaction()
    }

}
