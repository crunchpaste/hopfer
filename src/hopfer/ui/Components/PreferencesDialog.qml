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

    flags: Qt.FramelessWindowHint | Qt.SubWindow

    property bool isNative: false
    property bool darkTheme: false
    property int accent: 0
    property string version: "0.13.0"

    signal toggleNative(bool state)
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
            LabeledSwitch {
              text: "Dark theme"
              value: root.darkTheme
              onInteraction: root.toggleTheme(value)
            }
            AccentSelector {
                selectedIndex: root.accent
                onAccentSelected: (index) => {root.accentSelected(index)}
            }
            LabeledSwitch {
              visible: false
              text: "Use system frame"
              value: root.isNative
              onInteraction: root.toggleNative(value)
            }
          }
        }
        Item {
          Layout.fillWidth: true
          Layout.fillHeight: true
        }
    }
}
