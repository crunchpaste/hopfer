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
            "dynamic_range": dynamic_range.value,
            "k_factor": k_factor.value,
            "p_factor": p_factor.value,
            "q_factor": q_factor.value
        };
    }

    LabeledSlider {
        id: block_size

        text: "Block size"
        from: 2
        to: 500
        step: 1
        value: 25
        default_value: 25
        precision: 0
        onInteraction: root.settingsChanged()
    }

    LabeledSlider {
        id: dynamic_range

        text: "Dynamic range"
        from: 0
        to: 1
        step: 0.01
        value: 0.5
        default_value: 0.5
        precision: 2
        onInteraction: root.settingsChanged()
    }

    LabeledSlider {
        id: k_factor

        text: "Local threshold"
        from: 0
        to: 1
        step: 0.01
        value: 0.25
        default_value: 0.25
        precision: 2
        onInteraction: root.settingsChanged()
    }

    LabeledSlider {
        id: p_factor

        text: "Exponential influence"
        from: 0
        to: 5
        step: 0.01
        value: 0.3
        default_value: 0.3
        precision: 2
        onInteraction: root.settingsChanged()
    }

    LabeledSlider {
        id: q_factor

        text: "Exponential decay"
        from: 0.1
        to: 10
        step: 0.1
        value: 1
        default_value: 1
        precision: 1
        onInteraction: root.settingsChanged()
    }

}
