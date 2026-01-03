import Components
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ColumnLayout {
    id: root

    signal settingsChanged()

    property alias serpentine: serpentine.value

    function handleSliderInteraction() {
        root.settingsChanged();
    }

    function getDict() {
        return {
            "diffusion_factor": diffusion_factor.value,
            "serpentine": serpentine.value,
            "hysteresis": hysteresis.value,
            "noise": noise.value
        };
    }

    LabeledSlider {
        id: diffusion_factor

        text: "Diffusion factor"
        from: 0
        to: 1
        step: 0.01
        value: 1
        default_value: 1
        precision: 2
        onInteraction: root.settingsChanged()
    }
    LabeledSlider {
        id: hysteresis

        text: "Hysteresis"
        from: 0
        to: 5
        step: 0.01
        value: 1
        default_value: 1
        precision: 2
        onInteraction: root.settingsChanged()
    }

    LabeledSwitch {
        id: serpentine

        text: "Serpentine"
        onInteraction: root.settingsChanged()
    }

    LabeledSwitch {
        id: noise

        text: "Prime with noise"
        onInteraction: root.settingsChanged()
    }

}
