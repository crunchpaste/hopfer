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
    // signal tb()
    signal openPreferences

    function enable_toolbar(state) {
        open.enabled = state;
        save.enabled = state;
        save_as.enabled = state;
        resize.enabled = state;
        invert.enabled = state;
        rot_r.enabled = state;
        rot_l.enabled = state;
        flip.enabled = state;
        fit.enabled = state;
    }

    width: 60

    ColorPicker {
        id: color_picker
        // transientParent: app_window
        modality: Qt.WindowModal
        // onAccepted: console.log("User acknowledged the error.")
    }

    Rectangle {
        anchors.fill: parent
        color: Qt.darker(Material.background, 1.1)
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 10
        anchors.topMargin: 5
        // Apply the specific margins here
        spacing: 10

        Item {
            height: 2
        }

        SquareButton {
            id: open

            onClicked: root.openClicked()
            ToolTip.text: "Open image"

            icon: Component {
                Open {}
            }
        }

        SquareButton {
            id: save

            onClicked: root.saveClicked()
            ToolTip.text: "Save image"
            enabled: false

            icon: Component {
                Save {}
            }
        }

        SquareButton {
            id: save_as

            onClicked: root.saveAsClicked()
            ToolTip.text: "Save image as"
            enabled: false

            icon: Component {
                SaveAs {}
            }
        }

        Item {
            height: 5
        }

        SquareButton {
            id: resize

            ToolTip.text: "Resize image"
            enabled: false

            icon: Component {
                Resize {}
            }
        }

        SquareButton {
            id: invert

            onClicked: bridge.invert()
            ToolTip.text: "Invert values"
            enabled: false

            icon: Component {
                Invert {}
            }
        }

        SquareButton {
            id: rot_r

            onClicked: bridge.rotate(true)
            ToolTip.text: "Rotate CW"
            enabled: false

            icon: Component {
                RotR {}
            }
        }

        SquareButton {
            id: rot_l

            onClicked: bridge.rotate(false)
            ToolTip.text: "Rotate CCW"
            enabled: false

            icon: Component {
                RotL {}
            }
        }

        SquareButton {
            id: flip

            onClicked: bridge.flip()
            ToolTip.text: "Flip horizontally"
            enabled: false

            icon: Component {
                Flip {}
            }
        }

        Item {
            height: 5
        }

        SquareButton {
            id: fit

            // onClicked: bridge.flip()
            ToolTip.text: "Fit image to viewbox"
            enabled: false

            onClicked: {
                root.fitImage();
            }

            icon: Component {
                Fit {}
            }
        }

        SquareButton {
            // id: fit

            ToolTip.text: "Display at actual size"
            enabled: true

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
            ToolTip.text: "Preferences"

            icon: Component {
                Preferences {}
            }
            onClicked: {
                root.openPreferences();
            }
        }
    }
}
