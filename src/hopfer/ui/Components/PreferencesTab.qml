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
    anchors.margins: 20
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
      text: "Use system frame"
      value: config.window.native_frame ? true : false
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
      value: config.style.theme == 0
      onInteraction: {
        console.log(value)
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
    MemoryButtons {
      Layout.fillWidth: true
      Layout.topMargin: 8
      onMemChanged: (value) => {
        config.options.memory_warning_threshold = value
      }
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
