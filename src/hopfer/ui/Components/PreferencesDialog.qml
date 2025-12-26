import Components
import Icons
import QtCore
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ApplicationWindow {
    id: root

    // property color startColor: "ghostwhite"
    // property alias currentColor: colorController.current_color

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
            // 1. Force the visual size
            Layout.preferredHeight: 150
            Layout.preferredWidth: height * (81 / 40) // width = height * ratio

            // 2. Center it vertically in the RowLayout
            Layout.alignment: Qt.AlignHCenter

            // 3. Remove the 'scale: 10' property
            fill: Material.foreground
            opacity: 0.9
        }
        Label {
            text: "v0.13.0"
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
