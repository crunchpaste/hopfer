import Components
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Controls.Material

Item {

  ColumnLayout {
    id: root

    property bool isNative: config.window.native_frame
    property bool darkTheme: config.style.theme == 0

    spacing: 10
    anchors.fill: parent

    Rectangle {
      id: alert
      visible: {
          let scaleChanged = (scaleButtons.currentScale !== config.window.ui_scale);

          let frameChanged = (nativeSwitch.value !== config.window.native_frame);

          return scaleChanged || frameChanged;
      }
      height: 48
      radius: 5
      Layout.fillWidth: true
      Layout.margins: 20
      Layout.bottomMargin: 0
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
          font.family: "Material Symbols Rounded Filled 48pt"
          text: "\ue000"
          font.pointSize: 18
          color: Material.accent
        }
      }
    }
    Pane {
        Layout.fillWidth: true
        Layout.margins: 20
        Layout.topMargin: 10
        Layout.bottomMargin: 0
        Material.elevation: 10
        padding: 24

        background: Rectangle {
            color: Qt.alpha(Material.foreground, 0.02)
            radius: 8
        }

        ColumnLayout {
            width: parent.width
            spacing: 8

            Label {
                text: "Appearance"
                font.bold: true
                font.pointSize: 10
                color: Material.accent
                Layout.bottomMargin: 5
                opacity: 0.75
            }
            LabeledSwitch {
              id: nativeSwitch
              text: "Use system frame"
              enabled: (Qt.platform.os != "windows")
              value: config.window.native_frame ? true : false
              onInteraction: {
                bridge.toggle_native(value)
              }
            }
            LabeledSwitch {
              text: "Dark theme"
              value: config.style.theme == 0
              onInteraction: {
                let index = 0
                if (value) {
                  index = 0
                } else {
                  index = 1
                }
                config.style.theme = index
              }
            }

            AccentSelector {
              Layout.topMargin: 5
              selectedIndex: config.style.accent
              onAccentSelected: (index) => {config.style.accent = index}
            }
            ScaleButtons {
              id: scaleButtons
                Layout.fillWidth: true
                Layout.topMargin: 8
                onUiScaleChanged: (value) => {
                    bridge.ui_scale(value)
                }
            }
        }
    }

    Pane {
        Layout.fillWidth: true
        Layout.margins: 20
        Layout.topMargin: 10
        Layout.bottomMargin: 0
        Material.elevation: 10
        padding: 24

        background: Rectangle {
            color: Qt.alpha(Material.foreground, 0.02)
            radius: 8
        }

        ColumnLayout {
            width: parent.width
            spacing: 8

            Label {
                text: "System"
                font.bold: true
                font.pointSize: 10
                color: Material.accent
                Layout.bottomMargin: 5
                opacity: 0.75
            }

            MemoryButtons {
                Layout.fillWidth: true
                Layout.topMargin: 8
                onMemChanged: (value) => {
                    config.options.memory_warning_threshold = value
                }
            }
        }
    }
    Item {
      Layout.fillWidth: true
      Layout.fillHeight: true
    }
  }
}
