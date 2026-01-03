import Components
import Icons
import QtCore
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ApplicationWindow {
    id: root

    title: "Preferences"
    width: 520
    height: 700

    font.family: "Jetbrains Mono"
    font.pointSize: 11

    minimumWidth: width
    maximumWidth: width
    minimumHeight: height
    maximumHeight: height

    flags: isNative ? Qt.SubWindow : Qt.FramelessWindowHint | Qt.SubWindow

    property bool isNative: config.window.native_frame
    property bool darkTheme: false
    property int accent: 0
    property string version: config.version

    signal toggleTheme(bool state)
    signal accentSelected(int index)

    color: Material.background

    Shortcut {
        sequence: "Esc"
        onActivated: {
            root.close()
        }
    }

    ColumnLayout {
        anchors.fill: parent

        DialogTitlebar {
            visible: !root.isNative
            window: root
            title: "Preferences"
            Layout.fillWidth: true
            Layout.preferredHeight: 45
        }

        TitlebarIcon {
            id: logo
            Layout.preferredHeight: 150
            Layout.preferredWidth: height * (81 / 40) // width = height * ratio

            Layout.alignment: Qt.AlignHCenter

            fill: Material.foreground
            opacity: 0.9
        }
        Label {
            text: `v${root.version}`
            Layout.alignment: Qt.AlignHCenter
            font.family: "Jetbrains Mono"
            font.pointSize: 11
        }

        Item {height:24}

        TabBar {
            id: bar
            currentIndex: stack.currentIndex
            topPadding: 10

            Layout.fillWidth: true

            TabButton {
                text: "Preferences"
            }

            TabButton {
                text: "Shortcuts"
            }

            TabButton {
                text: "About"
            }

        }
        StackLayout {
            id: stack
            currentIndex: bar.currentIndex
            Layout.margins: 20
            ColumnLayout {
                spacing: 10
                // TODO: Implement UI scaling
                // LabeledSlider {
                //     text: "Font size"
                //     from: 8
                //     to: 14
                //     step: 0.1
                //     value: 11
                //     default_value: 11
                //     precision: 1
                //     onInteraction: (value) => {
                //       main_window.font.pointSize = value;
                //       root.font.pointSize = value;
                //     }
                // }
                LabeledSwitch {
                    // visible: false
                    text: "Use system frame"
                    value: root.isNative
                    onInteraction: {
                        bridge.toggle_native(value)
                        if (root.isNative != value) {
                            alert.visible = true
                        } else {
                            alert.visible = false
                        }
                    }
                }
                LabeledSwitch {
                    text: "Dark theme"
                    value: root.darkTheme
                    onInteraction: root.toggleTheme(value)
                }

                AccentSelector {
                    Layout.topMargin: 5
                    selectedIndex: root.accent
                    onAccentSelected: (index) => {root.accentSelected(index)}
                }
                Item {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                }
                Rectangle {
                    id: alert
                    visible: false
                    height: 48
                    radius: 5
                    Layout.fillWidth: true
                    color: Qt.darker(Material.background, 1.25)
                    RowLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        anchors.leftMargin: 16
                        anchors.rightMargin: 16
                        Label {
                            text: "Changes will take effect after a restart"
                            wrapMode: Text.WordWrap
                        }
                        Item {
                            Layout.fillWidth: true
                        }
                        Label {
                            font.family: "Material Icons"
                            text: "\ue000"
                            font.pointSize: 18
                            color: Material.accent
                        }
                    }
                }
            }
        }
    }
}
