import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import Settings

ColumnLayout {
    id: root
    property bool isReady: false

    signal halftoneChanged(string algorithm, var settings)

    Component { id: none; Item {} }
    Component { id: threshold; Threshold {} }
    Component { id: niblack; Niblack {} }
    Component { id: sauvola; Sauvola {} }
    Component { id: phansalkar; Phansalkar {} }
    Component { id: mezzo; Mezzo {} }
    Component { id: floydsteinberg; FloydSteinberg {} }

    property var componentMap: [
        none,
        threshold,
        niblack,
        sauvola,
        phansalkar,
        mezzo,
        floydsteinberg,
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

    Layout.margins: 20
    spacing: 18

    ComboBox {
        id: combo
        model: ["None", "Fixed threshold", "Niblack threshold", "Sauvola threshold", "Phansalkar threshold", "Mezzotint uniform", "Floyd-Steinberg"]

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
            width: combo.width
            height: Math.min(contentItem.implicitHeight, combo.Window.height)
            padding: 0

            contentItem: ListView {
                clip: true
                implicitHeight: contentHeight
                model: combo.popup.visible ? combo.delegateModel : null
                currentIndex: combo.highlightedIndex

                ScrollIndicator.vertical: ScrollIndicator { }
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
