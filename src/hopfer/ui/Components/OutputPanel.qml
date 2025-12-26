import Components
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Controls.Material

ColumnLayout {
    id: root
    property bool isReady: false
    // property alias grascale_enabled: combo.enabled
    signal colorsChanged(var settings)

    function toHex(c) {

        let r = Math.round(c.r * 255).toString(16).padStart(2, '0')
        let g = Math.round(c.g * 255).toString(16).padStart(2, '0')
        let b = Math.round(c.b * 255).toString(16).padStart(2, '0')

        return "#" + r + g + b
    }

    function updateColors() {
        let settings = {};

        settings = {
            "print": toHex(ink.color),
            "paper": toHex(paper.color),
            "alpha": toHex(alpha.color),
        }

        colorsChanged(settings);
    }


    Layout.topMargin: 20
    spacing: 10

    ColorControl{
        id: ink // print is an illegal name
        text: "Print"
        color: "#1C1B1F"
        onColorSelected: {
            root.updateColors()
        }
    }
    ColorControl{
        id: paper
        text: "Paper"
        color: "#FFFFFF"
        onColorSelected: {
            root.updateColors()
        }
    }
    ColorControl{
        id: alpha
        text: "Alpha"
        color: "#FA8072"
        onColorSelected: {
            root.updateColors()
        }
    }

    LabeledSwitch{
        id: eq
        text: "Output like preview"
        onInteraction: root.emitEnhanceSignal()
    }
    LabeledSwitch{
        id: norm
        text: "Discard alpha"
        onInteraction: root.emitEnhanceSignal()
    }

    Item {
        Layout.fillHeight: true
    }
}
