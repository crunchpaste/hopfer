import Components
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Controls.Material


ColumnLayout {
    id: root

    property bool isNative: false
    property bool darkTheme: false
    property int accent: 0

    signal toggleTheme(bool state)
    signal accentSelected(int index)

    spacing: 10
    // TODO: Implement UI scaling
    // LabeledSlider {
    //     text: "Font size"
    //     from: 8
    //     to: 14
    //     step: 0.1
    //     value: 11
    //     default_value: 11
    //     precision: 1
    //     onInteraction: (value) => {
    //       main_window.font.pointSize = value;
    //       root.font.pointSize = value;
    //     }
    // }
    LabeledSwitch {
        // visible: false
        text: "Use system frame"
        value: root.isNative
        onInteraction: {
            bridge.toggle_native(value)
            if (root.isNative != value) {
                alert.visible = true
            } else {
                alert.visible = false
            }
        }
    }
    LabeledSwitch {
        text: "Dark theme"
        value: root.darkTheme
        onInteraction: root.toggleTheme(value)
    }

    AccentSelector {
        Layout.topMargin: 5
        selectedIndex: root.accent
        onAccentSelected: (index) => {root.accentSelected(index)}
    }
    Item {
        Layout.fillWidth: true
        Layout.fillHeight: true
    }
    Rectangle {
        id: alert
        visible: false
        height: 48
        radius: 5
        Layout.fillWidth: true
        color: Qt.darker(Material.background, 1.25)
        RowLayout {
            anchors.fill: parent
            anchors.margins: 10
            anchors.leftMargin: 16
            anchors.rightMargin: 16
            Label {
                text: "Changes will take effect after a restart"
                wrapMode: Text.WordWrap
            }
            Item {
                Layout.fillWidth: true
            }
            Label {
                font.family: "Material Icons"
                text: "\ue000"
                font.pointSize: 18
                color: Material.accent
            }
        }
    }
}
