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
            "size": size.value,
            "perturbation": perturbation.value,
            "offset": offset.value
        };
    }

    LabeledSlider {
        id: size

        text: "Matrix size"
        from: 1
        to: 6
        step: 1
        value: 2
        default_value: 2
        precision: 0
        onInteraction: root.settingsChanged()
        // display the actual size, but use just the power under the hood
        valueText: 2 ** value.toFixed(precision)
    }

    LabeledSlider {
        id: perturbation

        text: "Perturbation"
        from: 0
        to: 0.5
        step: 0.01
        value: 0
        default_value: 0
        precision: 2
        onInteraction: root.settingsChanged()
    }

    LabeledSlider {
        id: offset

        text: "Matrix offset"
        from: -1
        to: 1
        step: 0.01
        value: 0
        default_value: 0
        precision: 2
        onInteraction: root.settingsChanged()
    }
}
