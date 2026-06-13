import Components
import QtCore
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

Window {
    id: root

    property color startColor: "ghostwhite"
    property alias currentColor: colorController.current_color
    property int isNative: (Qt.platform.os === "windows") ? true : config.window.native_frame

    signal colorAccepted(color newColor)

    title: "Select Color"
    width: Math.floor(880 * config.window.ui_scale)
    height: Math.floor((isNative ? 595 - tb.height : 595) * config.window.ui_scale)

    function center() {
        let mwx = config.window.x
        let mwy = config.window.y
        let mww = config.window.width
        let mwh = config.window.height
        x = mwx + (mww - width) / 2
        y = mwy + (mwh - height) / 2
    }
    onVisibleChanged: {
        if (visible) center()
    }


    function emitColor() {
        colorAccepted(colorController.current_color)
    }

    function toHex(c) {

        let r = Math.round(c.r * 255).toString(16).padStart(2, '0')
        let g = Math.round(c.g * 255).toString(16).padStart(2, '0')
        let b = Math.round(c.b * 255).toString(16).padStart(2, '0')

        return "#" + r + g + b
    }

    minimumWidth: width
    maximumWidth: width
    minimumHeight: height
    maximumHeight: height

    flags: isNative ? Qt.Window : Qt.FramelessWindowHint | Qt.SubWindow

    color: Material.background

    Shortcut {
        sequence: "Esc"
        onActivated: {
            root.close()
        }
    }

    Shortcut {
        sequences: ["Enter", "Return"]
        onActivated: {
            acceptButton.clicked()
        }
    }

    Item {
        id: colorController
        property color current_color: Qt.rgba(1, 0, 0, 1)
        property bool _isUpdating: false

        onCurrent_colorChanged: {
            if (_isUpdating) return
            _isUpdating = true
            hue_bar.hue = current_color.hsvHue
            sv_bar.saturation = current_color.hsvSaturation
            sv_bar.brightness = current_color.hsvValue
            _isUpdating = false
        }


        function updateFromRGB(r, g, b) {
            if (_isUpdating) return
            _isUpdating = true
            current_color = Qt.rgba(r / 255, g / 255, b / 255, 1.0)
            _isUpdating = false
        }
    }

    ColumnLayout {
        anchors.fill: parent

        DialogTitlebar {
            id: tb
            window: root
            title: "Select color"
            Layout.fillWidth: true
            Layout.preferredHeight: 45
            visible: !root.isNative
        }

        ScaleContainer {
            zoom: config.window.ui_scale
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: 20

            RowLayout {
                width: parent.width
                height: parent.height
                spacing: 20

                Rectangle {
                    id: hue_bar
                    property real hue: 0.0
                    width: 50
                    height: 500

                    gradient: Gradient {
                        GradientStop { position: 0.0; color: "#FF0000" }
                        GradientStop { position: 0.17; color: "#FFFF00" }
                        GradientStop { position: 0.33; color: "#00FF00" }
                        GradientStop { position: 0.5; color: "#00FFFF" }
                        GradientStop { position: 0.67; color: "#0000FF" }
                        GradientStop { position: 0.83; color: "#FF00FF" }
                        GradientStop { position: 1.0; color: "#FF0000" }
                    }
                    Rectangle {
                        id: handle
                        // Center the handle on the current value
                        y: (hue_bar.hue * hue_bar.height) - (height / 2)

                        width: parent.width
                        height: 3
                        radius: 0

                        color: "white"

                        Rectangle {
                          anchors.centerIn: parent
                          width: parent.width
                          height: 1
                          color: "black"
                        }

                    }
                    MouseArea {
                        anchors.fill: parent

                        function handleInput(mouse) {
                            let val = Math.max(0, Math.min(1, mouse.y / hue_bar.height))
                            hue_bar.hue = val

                            let newColor = Qt.hsva(hue_bar.hue, sv_bar.saturation, sv_bar.brightness, 1.0)
                            colorController.current_color = newColor
                        }

                        onPressed: (mouse) => handleInput(mouse)
                        onPositionChanged: (mouse) => handleInput(mouse)
                    }
                }

                Item {
                    id: sv_bar
                    width: 500
                    height: 500

                    clip: true

                    property real saturation: 0.0
                    property real brightness: 1.0

                    Rectangle {
                        anchors.fill: parent
                        color: Qt.hsva(hue_bar.hue, 1.0, 1.0, 1.0)
                    }


                    Rectangle {
                        anchors.fill: parent
                        gradient: Gradient {
                            orientation: Gradient.Horizontal
                            GradientStop {
                                position: 1.0
                                color: Qt.hsva(hue_bar.hue, 1.0, 1.0, 1.0)
                            }
                            GradientStop {
                                position: 0.0
                                color: "white"
                            }
                        }
                    }

                    Rectangle {
                        anchors.fill: parent
                        gradient: Gradient {
                            orientation: Gradient.Vertical
                            GradientStop {
                                position: 0.0
                                color: Qt.hsva(0.0, 0.0, 0.0, 0.0)
                            }
                            GradientStop {
                                position: 1.0
                                color: Qt.hsva(0.0, 0.0, 0.0, 1.0)
                            }
                        }
                    }
                    Item {
                        id: crosshair
                        // Map the property values to X and Y coordinates
                        x: sv_bar.saturation * sv_bar.width
                        y: (1.0 - sv_bar.brightness) * sv_bar.height

                        // Vertical Line (follows X)
                        Rectangle {
                            anchors.centerIn: parent
                            width: 3; height: sv_bar.height * 2 // Extra long for clipping
                            color: "white"
                            opacity: 0.6
                            Rectangle {
                                anchors.centerIn: parent; width: 1; height: parent.height; color: "black"
                            }
                        }

                        // Horizontal Line (follows Y)
                        Rectangle {
                            anchors.centerIn: parent
                            width: sv_bar.width * 2; height: 3
                            color: "white"
                            opacity: 0.6
                            Rectangle {
                                anchors.centerIn: parent; width: parent.width; height: 1; color: "black"
                            }
                        }
                    }

                    MouseArea {
                        anchors.fill: parent

                        function handleInput(mouse) {
                            sv_bar.saturation = Math.max(0, Math.min(1, mouse.x / sv_bar.width))
                            sv_bar.brightness = Math.max(0, Math.min(1, 1.0 - (mouse.y / sv_bar.height)))

                            let newColor = Qt.hsva(hue_bar.hue, sv_bar.saturation, sv_bar.brightness, 1.0)
                            colorController.current_color = newColor
                        }

                        onPressed: (mouse) => handleInput(mouse)
                        onPositionChanged: (mouse) => handleInput(mouse)
                    }

                }
                ColumnLayout {
                    id: sliders
                    Layout.margins: 0
                    Layout.maximumHeight: 500
                    spacing: 0

                    function handleSlider(mouse) {

                        let newColor = Qt.rgba(red.value/255, green.value/255, blue.value/255, 1.0)
                        colorController.current_color = newColor
                    }

                    Rectangle {
                        id: swatch
                        color: colorController.current_color
                        height: 250
                        width: 250

                        Rectangle {
                            id: textBackground
                            anchors.centerIn: parent

                            width: hexText.contentWidth + 20
                            height: hexText.contentHeight + 10

                            color: (Material.theme === Material.Light) ? "#40ffffff" : "#40000000"
                            opacity: 0.8
                            radius: 4

                            TextEdit {
                                id: hexText
                                anchors.centerIn: parent
                                text: toHex(colorController.current_color)
                                readOnly: true
                                selectByMouse: true
                                color: Material.foreground
                                font.family: "Jetbrains Mono"
                                font.pointSize: 11
                                cursorVisible: false
                                selectionColor: Material.accent
                                selectedTextColor: Material.background
                            }
                        }
                    }

                    Item {Layout.fillHeight: true}

                    LabeledSliderNR {
                        id: red
                        text: "Red"
                        from: 0
                        to: 255
                        step: 1
                        value: colorController.current_color.r * 255
                        default_value: root.startColor.r * 255
                        precision: 0
                        onMoved: sliders.handleSlider()
                    }
                    LabeledSliderNR {
                        id: green
                        text: "Green"
                        from: 0
                        to: 255
                        step: 1
                        value: colorController.current_color.g * 255
                        default_value: root.startColor.g * 255
                        precision: 0
                        onMoved: sliders.handleSlider()
                    }
                    LabeledSliderNR {
                        id: blue
                        text: "Blue"
                        from: 0
                        to: 255
                        step: 1
                        value: colorController.current_color.b * 255
                        default_value: root.startColor.b * 255
                        precision: 0
                        onMoved: sliders.handleSlider()
                    }

                    RoundButton {
                      id: acceptButton
                      text: "Accept"
                      implicitHeight: 40
                      topInset: 0
                      bottomInset: 0
                      leftInset: 0
                      rightInset: 0
                      Layout.fillWidth: true
                      radius: 5
                      font.family: "Jetbrains Mono"
                      font.pointSize: 11
                      onClicked: {
                        root.emitColor()
                        root.close() // Close the picker
                        }
                    }
                }
            }
        }
    }
}
