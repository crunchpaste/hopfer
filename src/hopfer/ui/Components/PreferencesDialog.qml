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

    property int isNative: config.window.native_frame

    flags: isNative ? Qt.SubWindow : Qt.FramelessWindowHint | Qt.SubWindow

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
            Layout.preferredWidth: height * (81 / 40)

            Layout.alignment: Qt.AlignHCenter

            fill: Material.foreground
            opacity: 0.9
        }
        Label {
            text: `v${config.version}`
            Layout.alignment: Qt.AlignHCenter
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
            PreferencesTab {}
            Item {}
            AboutTab {}
        }
    }
}
