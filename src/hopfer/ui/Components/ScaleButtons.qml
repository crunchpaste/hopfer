import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: root
    spacing: 10
    signal uiScaleChanged(real value)

    property real currentScale: scaleGroup.checkedButton ? scaleGroup.checkedButton.val : config.window.ui_scale

    ButtonGroup {
        id: scaleGroup
        onCheckedButtonChanged: {
            if (checkedButton) {
                root.uiScaleChanged(checkedButton.val)
            }
        }
    }

    RowLayout {
        spacing: 8
        Layout.fillWidth: true
        Label {
            text: "UI scale"
        }

        Item {
            Layout.fillWidth: true
        }

        Repeater {
            model: [
                { "label": "75%", "scale": 0.75 },
                { "label": "100%", "scale": 1.00 },
                { "label": "125%", "scale": 1.25 },
                { "label": "150%", "scale": 1.50 },
                { "label": "200%", "scale": 2.00 }
            ]

            delegate: RoundButton {
                text: modelData.label
                property real val: modelData.scale

                checkable: true
                autoExclusive: true
                ButtonGroup.group: scaleGroup

                checked: config.window.ui_scale == val
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
