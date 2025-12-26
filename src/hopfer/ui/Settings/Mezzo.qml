import Components
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ColumnLayout {
    id: root

    signal settingsChanged()

    function handleSliderInteraction() {
        root.settingsChanged();
    }

    function getDict() {
        return {
            "range": range.value,
            "seed": seed.value
        };
    }

    LabeledRange {
        id: range

        text: "Uniform range"
        from: 0
        to: 1
        step: 0.01
        value0: 0
        value1: 1
        precision: 2
        onInteraction: root.settingsChanged()
    }

    SpinBox {
        id: seed

        Layout.fillWidth: true
        editable: true
        from: 0
        to: 9999
        value: 3750
        onValueModified: root.settingsChanged()

        contentItem: TextField {
            text: seed.textFromValue(seed.value, seed.locale)
            validator: seed.validator
            readOnly: !seed.editable
            font.pointSize: 10.5
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            color: Material.foreground
            background: null
        }

    }

}
