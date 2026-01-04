import QtQuick

Item {
    id: root
    property var openDialog
    property var saveDialog
    property var tabBar
    property var viewer
    property var toolbar

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
      sequences: ["Cmd+I", "Ctrl+I"]
      onActivated: {
        bar.currentIndex = 0;
        image_panel.focusCombo();
      }
    }
    Shortcut {
      sequences: ["Cmd+H", "Ctrl+H"]
      onActivated: {
        bar.currentIndex = 1;
        halftone_panel.focusCombo();
      }
    }
    Shortcut {
      sequences: ["Cmd+E", "Ctrl+E"]
      onActivated: {
        bar.currentIndex = 2;
      }
    }
    Shortcut {
      sequences: ["Cmd+P", "Ctrl+P"]
      onActivated: {
        preferences.show();
        preferences.raise();
      }
    }
    Shortcut {
      sequences: ["Cmd+Shift+I", "Ctrl+Shift+I"]
      onActivated: {
        toolbar.resizeDialog.show();
        toolbar.resizeDialog.raise();
      }
    }
    Shortcut {
      sequences: ["Cmd+Shift+N", "Ctrl+Shift+N"]
      onActivated: {
        bridge.invert()
      }
    }
    Shortcut {
      sequences: ["Cmd+R", "Ctrl+R"]
      onActivated: {
        bridge.rotate(true)
      }
    }
    Shortcut {
      sequences: ["Cmd+Shift+R", "Ctrl+Shift+R"]
      onActivated: {
        bridge.rotate(false)
      }
    }
    Shortcut {
      sequences: ["Cmd+0", "Ctrl+0"]
      onActivated: {
        viewer.fit()
      }
    }
    Instantiator {
        model: 9

        Shortcut {
            readonly property int scaleValue: index + 1

            sequences: ["Cmd+" + scaleValue, "Ctrl+" + scaleValue]

            context: Qt.WindowShortcut

            onActivated: {
                root.viewer.to_scale(scaleValue)
            }
        }
    }
}
