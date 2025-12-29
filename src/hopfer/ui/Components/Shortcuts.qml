import QtQuick

Item {
    id: root
    property var openDialog
    property var saveDialog
    property var tabBar
    property var viewer

    Shortcut {
      sequence: StandardKey.Open
      onActivated: {
        openDialog.open();
      }
    }
    Shortcut {
      sequence: StandardKey.Save
      onActivated: {
        if (bridge.has_image) {

          bridge.save(saveDialog.selectedFile);
        }
      }
    }
    Shortcut {
      sequence: StandardKey.SaveAs
      onActivated: {
        if (bridge.has_image) {
          saveDialog.open();
        }
      }
    }
    Shortcut {
      sequences: [StandardKey.Copy]
      onActivated: {
        bridge.save_to_clipboard();
      }
    }
    Shortcut {
      sequences: [StandardKey.Paste]
      onActivated: {
        bridge.open_clipboard();
      }
    }
    Shortcut {
      sequence: (Qt.platform.os === "osx") ? "Cmd+I" : "Ctrl+I"
      onActivated: {
        bar.currentIndex = 0;
        image_panel.focusCombo();
      }
    }
    Shortcut {
      sequence: (Qt.platform.os === "osx") ? "Cmd+H" : "Ctrl+H"
      onActivated: {
        bar.currentIndex = 1;
        halftone_panel.focusCombo();
      }
    }
    Shortcut {
      sequence: (Qt.platform.os === "osx") ? "Cmd+E" : "Ctrl+E"
      onActivated: {
        bar.currentIndex = 2;
      }
    }
    Shortcut {
      sequence: (Qt.platform.os === "osx") ? "Cmd+P" : "Ctrl+P"
      onActivated: {
        preferences.show();
        preferences.raise();
      }
    }
    Shortcut {
      sequence: (Qt.platform.os === "osx") ? "Cmd+0" : "Ctrl+0"
      onActivated: {
        viewer.fit()
      }
    }
    Instantiator {
        model: 9

        Shortcut {
            readonly property int scaleValue: index + 1

            sequence: (Qt.platform.os === "osx") ?
                      "Cmd+" + scaleValue :
                      "Ctrl+" + scaleValue

            context: Qt.WindowShortcut

            onActivated: {
                root.viewer.to_scale(scaleValue)
            }
        }
    }
}
