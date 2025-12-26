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
            "threshold": threshold.value
        };
    }

    LabeledSlider {
        id: threshold

        text: "Threshold value"
        from: 0
        to: 1
        step: 0.01
        value: 0.5
        default_value: 0.5
        precision: 2
        onInteraction: root.settingsChanged()
    }

}
