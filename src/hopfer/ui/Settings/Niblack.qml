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
            "block_size": block_size.value,
            "k_factor": k_factor.value
        };
    }

    LabeledSlider {
        id: block_size

        text: "Block size"
        from: 2
        to: 500
        step: 1
        value: 5
        default_value: 5
        precision: 0
        onInteraction: root.settingsChanged()
    }

    LabeledSlider {
        id: k_factor

        text: "Local threshold"
        from: 0
        to: 1
        step: 0.01
        value: 0.1
        default_value: 0.1
        precision: 2
        onInteraction: root.settingsChanged()
    }

}
