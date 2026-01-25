import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import Settings

ColumnLayout {
    id: root
    property bool isReady: false

    signal halftoneChanged(string algorithm, var settings)

    Component { id: none; BlankSettings {} }
    Component { id: threshold; Threshold {} }
    Component { id: niblack; Niblack {} }
    Component { id: sauvola; Sauvola {} }
    Component { id: phansalkar; Phansalkar {} }
    Component { id: mezzo; Mezzo {} }
    Component { id: clustered; Clustered {} }
    Component { id: errordiffusion; ErrorDiffusion {} }
    Component { id: errordiffusion_s; ErrorDiffusion {serpentine: true} }
    Component { id: levien; Levien {serpentine: true} }
    Component { id: nakano; Nakano {serpentine: true} }

    property var componentMap: [
        none,
        threshold,
        niblack,
        sauvola,
        phansalkar,
        mezzo,
        clustered,
        errordiffusion,
        errordiffusion,
        errordiffusion,
        errordiffusion,
        errordiffusion,
        errordiffusion,
        errordiffusion,
        errordiffusion,
        errordiffusion,
        errordiffusion,
        errordiffusion_s,
        errordiffusion_s,
        errordiffusion_s,
        levien,
        nakano,
    ]

    function emitChangeSignal(algorithm_name) {
        if (!isReady) return;
        let algorithm = algorithm_name;
        let settings = {};

        if (loader.item && loader.item.getDict) {
            settings = loader.item.getDict();
        } else {
            settings = {};
        }
        root.halftoneChanged(algorithm, settings);
    }
    function focusCombo() {
        combo.forceActiveFocus();
    }

    Layout.margins: 20
    spacing: 18

    ComboBox {
        id: combo
        model: [
            "None",
            "Fixed threshold",
            "Niblack threshold",
            "Sauvola threshold",
            "Phansalkar threshold",
            "Mezzotint uniform",
            "Clustered dot",
            "Floyd-Steinberg",
            "False Floyd-Steinberg",
            "Jarvis",
            "Stucki",
            "Stucki small",
            "Stucki large",
            "Atkinson",
            "Burkes",
            "Sierra",
            "Sierra2",
            "Sierra2 4A",
            "Ostromoukhov",
            "Zhou-Fang",
            "Levien",
            "Nakano",
            ]

        onCurrentIndexChanged: {
            let new_algorithm = combo.valueAt(combo.currentIndex);

            Qt.callLater(function() {
                root.emitChangeSignal(new_algorithm)
            })
        }

        Component.onCompleted: {
            Qt.callLater(() => { isReady = true; })
        }

        Layout.fillWidth: true
        popup: Popup {

           y: 0

           id: comboPopup

           width: combo.width * config.window.ui_scale

           height: Math.min(list.implicitHeight * config.window.ui_scale, combo.Window.height - (150 * config.window.ui_scale) )
           padding: 0
           // clip: true
           contentItem: Item{
               width: comboPopup.height / config.window.ui_scale
               height: comboPopup.height / config.window.ui_scale
               transform: Scale {
                   xScale: config.window.ui_scale
                   yScale: config.window.ui_scale
                   origin.x: 0; origin.y: 0
               }
               ListView {
                   id: list
                   clip: true
                   implicitHeight: contentHeight
                   width: parent.width / config.window.ui_scale
                   height: parent.height / config.window.ui_scale
                   model: combo.popup.visible ? combo.delegateModel : null
                   currentIndex: combo.highlightedIndex
                   ScrollIndicator.vertical: ScrollIndicator { }
               }
           }

           background: Rectangle {

               color: Material.background

               border.color: Material.accent

               border.width: 2

               radius: 5
           }
       }
    }

    Loader {
        id: loader
        // Layout.margins: 5
        Layout.fillWidth: true
        sourceComponent: root.componentMap[combo.currentIndex]
    }

    Item {
        Layout.fillHeight: true
    }

    Connections {
        id: signalConnector

        target: loader.item

        function onSettingsChanged() {
            root.emitChangeSignal(combo.valueAt(combo.currentIndex));
        }
    }
}
