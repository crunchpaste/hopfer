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
            "location": location.value,
            "std": std.value,
            "seed": seed.value
        };
    }

    LabeledSlider {
        id: location

        text: "Peak location"
        from: 0
        to: 1
        step: 0.01
        value: 0.5
        default_value: 0.5
        precision: 2
        onInteraction: root.settingsChanged()
    }

    LabeledSlider {
        id: std

        text: "Standard deviation"
        from: 0
        to: 0.5
        step: 0.01
        value: 0.2
        default_value: 0.2
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
