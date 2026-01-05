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
    height: 740

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
    signal memChanged(int value)

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
            PreferencesTab {
                isNative: root.isNative
                darkTheme: root.darkTheme
                accent: root.accent

                onToggleTheme: (state) => root.toggleTheme(state)
                onAccentSelected: (index) => root.accentSelected(index)
                onMemChanged: (value) => root.memChanged(value)
            }
            Item {}
            AboutTab {}
        }
    }
}
