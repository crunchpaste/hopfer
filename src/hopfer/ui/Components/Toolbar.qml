import Icons
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

Item {
    id: root

    signal openClicked
    signal saveAsClicked
    signal saveClicked
    signal fitImage
    signal actual
    signal openPreferences

    property bool buttonsEnabled: bridge.has_image
    property alias resizeDialog: resizeDialog

    width: 60

    ResizeDialog {
        id: resizeDialog
        modality: Qt.ApplicationModal
    }

    Rectangle {
        anchors.fill: parent
        color: Qt.darker(Material.background, 1.1)
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        anchors.topMargin: 5
        spacing: 10

        Item {
            height: 2
        }

        SquareButton {
            id: open

            onClicked: root.openClicked()
            ToolTip.text: "Open image (Ctrl+0)"

            icon: Component {
                Open {}
            }
        }

        SquareButton {
            id: save

            onClicked: root.saveClicked()
            ToolTip.text: "Save image (Ctrl+S)"
            enabled: root.buttonsEnabled

            icon: Component {
                Save {}
            }
        }

        SquareButton {
            id: save_as

            onClicked: root.saveAsClicked()
            ToolTip.text: "Save image as (Ctrl+Shift+S)"
            enabled: root.buttonsEnabled

            icon: Component {
                SaveAs {}
            }
        }

        Item {
            height: 5
        }

        SquareButton {
            id: resize

            ToolTip.text: "Resize image (Ctrl+Shift+I)"
            enabled: root.buttonsEnabled

            icon: Component {
                Resize {}
            }
            onClicked: {
              resizeDialog.show()
              resizeDialog.raise()
            }
        }

        SquareButton {
            id: invert

            onClicked: bridge.invert()
            ToolTip.text: "Invert values (Ctrl+Shift+N)"
            enabled: root.buttonsEnabled

            icon: Component {
                Invert {}
            }
        }

        SquareButton {
            id: rot_r

            onClicked: bridge.rotate(true)
            ToolTip.text: "Rotate CW (Ctrl+R)"
            enabled: root.buttonsEnabled

            icon: Component {
                RotR {}
            }
        }

        SquareButton {
            id: rot_l

            onClicked: bridge.rotate(false)
            ToolTip.text: "Rotate CCW (Ctrl+Shift+R)"
            enabled: root.buttonsEnabled

            icon: Component {
                RotL {}
            }
        }

        SquareButton {
            id: flip

            ToolTip.text: "Flip horizontally (Ctrl+F)"
            enabled: root.buttonsEnabled

            onClicked: bridge.flip()

            icon: Component {
                Flip {}
            }
        }

        Item {
            height: 5
        }

        SquareButton {
            id: fit

            ToolTip.text: "Fit image to viewbox (Ctrl+0)"
            enabled: root.buttonsEnabled

            onClicked: {
                root.fitImage();
            }

            icon: Component {
                Fit {}
            }
        }

        SquareButton {
            id: actual

            ToolTip.text: "Display at actual size (Ctrl+1)"
            enabled: root.buttonsEnabled

            onClicked: {
                root.actual();
            }

            icon: Component {
                View {}
            }
        }

        Item {
            Layout.fillHeight: true
        }

        SquareButton {
            ToolTip.text: "Preferences (Ctrl+P)"

            icon: Component {
                Preferences {}
            }
            onClicked: {
                root.openPreferences();
            }
        }
    }
}
