import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: root
    spacing: 10
    signal memChanged(int value)

    ButtonGroup {
        id: ramGroup
        onCheckedButtonChanged: {
            if (checkedButton) {
                root.memChanged(checkedButton.val)
            }
        }
    }

    RowLayout {
        spacing: 8
        Layout.fillWidth: true
        Label {
            text: "Memory warning"
        }

        Item {
            Layout.fillWidth: true
        }

        Repeater {
            model: [
                { "label": "1GB",   "mb": 1024 },
                { "label": "2GB",   "mb": 2048 },
                { "label": "4GB",   "mb": 4096 },
                { "label": "8GB",   "mb": 8192 },
                { "label": "Off", "mb": -1 }
            ]

            delegate: RoundButton {
                text: modelData.label
                property int val: modelData.mb

                checkable: true
                autoExclusive: true
                ButtonGroup.group: ramGroup

                checked: config.options.memory_warning_threshold == val
                highlighted: checked
                topPadding: 4
                bottomPadding: 4
                leftPadding: 8
                rightPadding: 8
                topInset: 0
                bottomInset: 0
                leftInset: 0
                rightInset: 0
                radius: 5
                font.pointSize: 10
                contentItem: Label {
                    text: parent.text
                    font: parent.font
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    color: parent.checked ? Material.background : Material.foreground
                }
            }
        }
    }
}
