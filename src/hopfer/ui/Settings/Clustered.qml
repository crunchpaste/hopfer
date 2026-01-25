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
            "size": dot_size.value,
        };
    }

    LabeledSlider {
        id: dot_size

        text: "Dot size"
        from: 2
        to: 150
        step: 1
        value: 15
      default_value: 15
        precision: 0
        onInteraction: root.settingsChanged()
    }
}
