import Components
import Icons
import QtCore
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ApplicationWindow {
    id: root

    title: "Resize image"
    width: 600
    height: 380

    font.family: "Jetbrains Mono"
    font.pointSize: 11

    minimumWidth: width
    maximumWidth: width
    minimumHeight: height
    maximumHeight: height

    flags: isNative ? Qt.SubWindow : Qt.FramelessWindowHint | Qt.SubWindow

    property bool isNative: config.window.native_frame
    property int memThresh: config.options.memory_warning_threshold
    property int pixelW: bridge.width
    property int pixelH: bridge.height
    property real ratio: bridge.ratio
    property int res: 300

    color: Material.background

    function getUnitFactor() {
        let unit = unitCombo.currentText
        let resType = resCombo.currentText

        if (unit === "px") return 1.0

        let dpi = root.res

        let effectiveDpi = dpi

        if (resType === "px/cm") {
            effectiveDpi = dpi * 2.54
        } else if (resType === "px/mm") {
            effectiveDpi = dpi * 25.4
        }

        if (unit === "inch") return effectiveDpi
        if (unit === "cm") return effectiveDpi / 2.54
        if (unit === "mm") return effectiveDpi / 25.4

        return 1.0
    }

    function sendResize() {
        bridge.send_resize(
            root.pixelW,
            root.pixelH,
            interpolationCombo.currentText
        )
        root.close()
    }

    function getMemoryEstimate() {
        let w = root.pixelW
        let h = root.pixelH
        let channels = 3
        let bytesPerPixel = (channels * 2) + 5
        let totalBytes = w * h * bytesPerPixel
        let conservativeMB = (totalBytes * 2) / (1024 * 1024)
        return conservativeMB
    }

    function resetValues() {
        // Runs when the dialog is cancelled
        root.pixelW = bridge.width
        root.pixelH = bridge.height
        root.ratio = bridge.ratio
        root.res = 150

        unitCombo.currentIndex = 0
        resCombo.currentIndex = 0
    }

    Connections {
        target: bridge
        function onSizeChanged() {
            root.pixelW = bridge.width
            root.pixelH = bridge.height
            root.ratio = bridge.ratio
        }
    }

    Shortcut {
        sequence: "Esc"
        onActivated: {
            resetValues()
            root.close()
        }
    }

    Dialog {
        id: dialog
        modal: true
        standardButtons: Dialog.Ok | Dialog.Cancel
        anchors.centerIn: parent
        width: parent.width * 0.9
        title: "Memory warning"

        onAccepted: {
            root.sendResize()
            root.close()
        }
        ColumnLayout {
            spacing: 15
            width: parent.width

            Label {
                text: "The requested dimensions will take up a significant amount of memory:"
                Layout.maximumWidth: parent.width
                wrapMode: Text.WordWrap
            }

            Label {
                property real mb: root.getMemoryEstimate()
                text: `Estimated peak memory usage: ${mb.toFixed(1)} MB`
                Layout.maximumWidth: parent.width
                color: Material.accent
                wrapMode: Text.WordWrap
            }

            Label {
                text: "Please ensure your system has enough free memory before continuing. Exceeding your available RAM can lead to a system freeze."
                Layout.maximumWidth: parent.width
                wrapMode: Text.WordWrap
                Layout.fillWidth: true
                opacity: 0.7
            }
        }
    }

    ColumnLayout {
        anchors.fill: parent

        DialogTitlebar {
            visible: !root.isNative
            window: root
            title: root.title
            Layout.fillWidth: true
            Layout.preferredHeight: 45
        }
        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true
        }
        GridLayout {
            columns: 4
            rows: 4
            uniformCellHeights: true
            rowSpacing: 10
            columnSpacing: 10
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: 20

            // THE LABELS
            Label {
                text: "Width"
                Layout.column: 0
                Layout.row: 0
            }
            Label {
                text: "Height"
                Layout.column: 0
                Layout.row: 1
            }
            Label {
                text: "Resolution"
                Layout.column: 0
                Layout.row: 2
            }
            Label {
                text: "Interpolation"
                Layout.column: 0
                Layout.row: 3
            }
            // SPINBOXES HERE
            MathSpinBox {
                id: widthSpin
                Layout.column: 1; Layout.row: 0; Layout.fillWidth: true
                decimals: unitCombo.model.get(unitCombo.currentIndex).decimals
                from: 1
                to: 1000000
                value: Math.round((root.pixelW / getUnitFactor()) * factor)

                onValueModified: {
                    root.pixelW = Math.round((value / factor) * getUnitFactor())
                    if (ratioLockButton.isLocked) {
                        root.pixelH = Math.floor(root.pixelW * root.ratio)
                    }
                }
            }

            // HEIGHT
            MathSpinBox {
                id: heightSpin
                Layout.column: 1; Layout.row: 1; Layout.fillWidth: true
                decimals: unitCombo.model.get(unitCombo.currentIndex).decimals
                from: 1
                to: 1000000
                value: Math.round((root.pixelH / getUnitFactor()) * factor)

                onValueModified: {
                    root.pixelH = Math.round((value / factor) * getUnitFactor())
                    if (ratioLockButton.isLocked) {
                        root.pixelW = Math.floor(root.pixelH / root.ratio)
                    }
                }
            }

            // RESOLUTION
            MathSpinBox {
                id: resSpin
                Layout.column: 1; Layout.row: 2; Layout.fillWidth: true
                decimals: 0
                from: 1
                to: 10000
                value: root.res

                onValueModified: {
                    root.res = value
                }
            }
            RoundButton {
                id: ratioLockButton
                property bool isLocked: true
                Layout.column: 2
                Layout.row: 0
                Layout.rowSpan: 2
                Layout.preferredWidth: 50
                Layout.alignment: Qt.AlignVCenter

                activeFocusOnTab: false

                width: 50
                height: 50

                flat: true
                checkable: true
                checked: isLocked

                contentItem: Label {
                    text: ratioLockButton.checked ? "\ue897" : "\uf656"
                    font.pixelSize: 18
                    font.family: "Material Icons"
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
                onClicked: isLocked = !isLocked
            }
            // COMBOS
            ComboBox {
                id: unitCombo
                Layout.column: 3
                Layout.row: 0
                Layout.rowSpan: 2
                Layout.preferredWidth: 100

                activeFocusOnTab: false

                textRole: "unit"

                model: ListModel {
                    ListElement { unit: "px";   decimals: 0 }
                    ListElement { unit: "inch"; decimals: 3 }
                    ListElement { unit: "cm";   decimals: 3 }
                    ListElement { unit: "mm";   decimals: 2 }
                }
            }
            ComboBox {
                id: resCombo
                Layout.column: 3
                Layout.row: 2
                Layout.preferredWidth: 100

                activeFocusOnTab: false

                textRole: "unit"

                model: ListModel {
                    ListElement { unit: "px/in" }
                    ListElement { unit: "px/cm" }
                    ListElement { unit: "px/mm" }
                }
            }
            ComboBox {
                id: interpolationCombo
                Layout.column: 1
                Layout.row: 3
                Layout.columnSpan: 3
                Layout.fillWidth: true

                textRole: "unit"

                model: ListModel {
                    ListElement {
                      unit: "Nearest neighbor";
                    }
                    ListElement {
                      unit: "Bilinear";
                    }
                    ListElement {
                      unit: "Bicubic";
                    }
                    ListElement {
                      unit: "Lanczos";
                    }
                }
            }
        }
        RowLayout{
            Layout.margins: 20
            Layout.topMargin: 0
            spacing: 20
            Item {
                Layout.fillWidth: true
            }
            RoundButton {
                radius: 5
                implicitHeight: 40
                implicitWidth: 120
                text: "Cancel"
                topInset: 0
                bottomInset: 0
                leftInset: 0
                rightInset: 0

                activeFocusOnTab: false

                onClicked: {
                  root.resetValues()
                  root.close()
                }
            }
            RoundButton {
                id: acceptButton
                radius: 5
                implicitHeight: 40
                implicitWidth: 120
                text: "Resize"
                topInset: 0
                bottomInset: 0
                leftInset: 0
                rightInset: 0
                onClicked: {
                    // let free_ram = bridge.get_free_ram()
                    let estimate = root.getMemoryEstimate()
                    let thresh = root.memThresh
                    if (estimate > thresh && thresh > 0) {
                        dialog.open()
                    } else {
                        root.sendResize()
                    }
                }
            }
        }
    }
}
