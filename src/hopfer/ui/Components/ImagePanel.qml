import Components
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import Settings

ColumnLayout {
    id: root
    property bool isReady: false
    property alias grascale_enabled: combo.enabled

    signal grayscaleChanged(string algorithm, var settings)
    signal enhanceChanged(var settings)

    function emitGrayscaleSignal(algorithm) {
        if (!isReady) return;
        let settings = {};
        settings = {
            "r": red.value,
            "g": green.value,
            "b": blue.value
        }
        grayscaleChanged(algorithm, settings);
    }

    function emitEnhanceSignal() {
        if (!isReady) return;
        let algorithm = combo.valueAt(combo.currentIndex)
        let settings = {};

        settings = {
            "normalize": norm.value,
            "equalize": eq.value,
            "bc_t": bc.value,
            "blur_t": bd.value,
            "unsharp_t": um.value,
            "laplacian_t": lap.value,
            "brightness": brightness.value,
            "contrast": contrast.value,
            "box": box.value,
            "blur": gauss.value,
            "median": median.value,
            "u_radius": um_rad.value,
            "u_strength": um_str.value,
            "u_thresh": um_thresh.value,
            "l_strength": lap_str.value,
        }

        root.enhanceChanged(settings);
    }

    function focusCombo() {
        combo.forceActiveFocus();
    }

    Layout.topMargin: 20
    spacing: 18

    ComboBox {
        id: combo
        model: ["Luminance", "Luma", "Lightness", "Average", "Value", "Manual RGB"]

        onCurrentIndexChanged: {
            Qt.callLater(function() {
                let algorithm = combo.valueAt(combo.currentIndex)
                root.emitGrayscaleSignal(algorithm)
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
    ColumnLayout {
        visible: combo.valueAt(combo.currentIndex) == "Manual RGB"
        LabeledSlider {
            id: red
            // visible: combo.valueAt(combo.currentIndex) == "Manual RGB"
            text: "Red"
            from: 0
            to: 1
            step: 0.01
            value: 0.33
            default_value: 0.33
            precision: 2
            onInteraction: root.emitGrayscaleSignal(combo.valueAt(combo.currentIndex))
        }
        LabeledSlider {
            id: green
            // visible: combo.valueAt(combo.currentIndex) == "Manual RGB"
            text: "Green"
            from: 0
            to: 1
            step: 0.01
            value: 0.33
            default_value: 0.33
            precision: 2
            onInteraction: root.emitGrayscaleSignal(combo.valueAt(combo.currentIndex))
        }
        LabeledSlider {
            id: blue
            // visible: combo.valueAt(combo.currentIndex) == "Manual RGB"
            text: "Blue"
            from: 0
            to: 1
            step: 0.01
            value: 0.33
            default_value: 0.33
            precision: 2
            onInteraction: root.emitGrayscaleSignal(combo.valueAt(combo.currentIndex))
        }
    }
    ScrollView {
        id: scrollFrame
        Layout.fillWidth: true
        Layout.fillHeight: true
        Layout.margins: -10
        contentWidth: availableWidth
        clip: false
        ScrollBar.vertical.policy: ScrollBar.AlwaysOff

        ColumnLayout {
            id: settings
            anchors.fill: parent
            anchors.margins: 10
            anchors.bottomMargin: 0
            spacing: 10
            LabeledSwitch{
              id: norm
              text: "Normalize histogram"
              onInteraction: root.emitEnhanceSignal()
            }
            LabeledSwitch{
              id: eq
              text: "Equalize histogram"
              onInteraction: root.emitEnhanceSignal()
            }
            LabeledSwitch{
              id: bc
              text: "Brightness/contrast"
              onInteraction: function() {
                  if (brightness.value != brightness.default_value ||
                      contrast.value != contrast.default_value) {

                      root.emitEnhanceSignal()
                  }
              }
            }
            ColumnLayout {

                visible: bc.value
                Layout.margins: 10
                Layout.fillWidth: true

                LabeledSlider {
                    id: brightness
                    text: "Brightness"
                    from: -1
                    to: 1
                    step: 0.01
                    value: 0
                    default_value: 0
                    precision: 2
                    onInteraction: root.emitEnhanceSignal()
                }
                LabeledSlider {
                    id: contrast
                    text: "Contrast"
                    from: -1
                    to: 1
                    step: 0.01
                    value: 0
                    default_value: 0
                    precision: 2
                    onInteraction: root.emitEnhanceSignal()
                }
            }
            LabeledSwitch{
                id: bd
                text: "Blur/denoise"
                onInteraction: function() {
                    if (gauss.value != gauss.default_value ||
                        median.value != median.default_value) {

                        root.emitEnhanceSignal()
                    }
                }
                // onInteraction: root.emitEnhanceSignal()
            }

            ColumnLayout {

                visible: bd.value
                Layout.margins: 10
                Layout.fillWidth: true

                LabeledSlider {
                    id: median
                    text: "Median filter"
                    from: 1
                    to: 50
                    step: 1
                    value: 1
                    default_value: 1
                    precision: 1
                    onInteraction: root.emitEnhanceSignal()
                }
                LabeledSlider {
                    id: box
                    text: "Box blur"
                    from: 0
                    to: 50
                    step: 1
                    value: 0
                    default_value: 0
                    precision: 0
                    onInteraction: root.emitEnhanceSignal()
                }
                LabeledSlider {
                    id: gauss
                    text: "Gaussian filter"
                    from: 0
                    to: 150
                    step: 1
                    value: 0
                    default_value: 0
                    precision: 0
                    onInteraction: root.emitEnhanceSignal()
                }
            }
            LabeledSwitch {
              id: um
              text: "Unsharp mask"
              onInteraction: root.emitEnhanceSignal()
            }
            ColumnLayout {

                visible: um.value
                Layout.margins: 10
                Layout.fillWidth: true

                LabeledSlider {
                    id: um_rad
                    text: "Radius"
                    from: 0
                    to: 10
                    step: 0.1
                    value: 3
                    default_value: 3
                    precision: 1
                    onInteraction: root.emitEnhanceSignal()
                }
                LabeledSlider {
                    id: um_str
                    text: "Strength"
                    from: 0
                    to: 1
                    step: 0.01
                    value: 0.25
                    default_value: 0.25
                    precision: 2
                    onInteraction: root.emitEnhanceSignal()
                }
                LabeledSlider {
                    id: um_thresh
                    text: "Threshold"
                    from: 0
                    to: 1
                    step: 0.01
                    value: 0.3
                    default_value: 3
                    precision: 1
                    onInteraction: root.emitEnhanceSignal()
                }
            }
            LabeledSwitch{
              id: lap
              text: "Laplacian sharpening"
              onInteraction: root.emitEnhanceSignal()
            }
            ColumnLayout {

                visible: lap.value
                Layout.margins: 10
                Layout.fillWidth: true

                LabeledSlider {
                    id: lap_str
                    text: "Strength"
                    from: 0
                    to: 1
                    step: 0.01
                    value: 0.25
                    default_value: 0.25
                    precision: 2
                    onInteraction: root.emitEnhanceSignal()
                }
            }
            Item {height: 5}
        }
    }




    Item {
        Layout.fillHeight: true
    }
}
