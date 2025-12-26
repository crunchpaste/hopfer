import Components
import Icons
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import QtQuick.Effects

Rectangle {
    id: root
    color: Qt.darker(Material.background, 1.15)
    required property Window app_window
    opacity: app_window.active ? 1.0 : 0.5
    height: 45
    // width: app_window.width
    layer.enabled: true
    layer.effect: MultiEffect {
        shadowEnabled: true
        shadowColor: "black"
        shadowBlur: 0.4      // How soft the shadow is
        shadowVerticalOffset: 3  // Moves the shadow down
        shadowOpacity: 0.3
    }
    function min_max() {
      if (app_window.visibility === Window.Maximized)
      app_window.showNormal()
      else
      app_window.showMaximized()
    }
    Behavior on width {
        // Disable the animation if the window is currently being resized
        // enabled: !main_window.isResizing
        NumberAnimation { duration: 0 }
    }

    RowLayout {
        z: 10
        anchors.fill: parent
        anchors.leftMargin: 15
        anchors.rightMargin: 10
        TitlebarIcon { fill:Material.foreground; opacity:0.9 }
        Item { Layout.fillWidth: true }
        TitlebarButton {
            icon: Component {Minimize{}}
            onClicked: app_window.showMinimized()
        }
        TitlebarButton {
            id: expand
            Component {
                id: expandIcon
                Expand {}
            }

            Component {
                id: collapseIcon
                Collapse {}
            }
            icon: app_window.visibility == Window.Maximized ? collapseIcon : expandIcon
            onClicked: root.min_max()
        }
        TitlebarButton {
            icon: Component {Close{}}
            onClicked: Qt.quit()
        }

    }

    DragHandler {
        target: null
        onActiveChanged: if (active) app_window.startSystemMove()
    }

    // Double click to maximize
    MouseArea {
        anchors.fill: parent
        // Ensure this sits BELOW the buttons so they still work
        // z: -1

        // We don't want to block the DragHandler from seeing the press,
        // but MouseArea.onDoubleClicked is a specialized event.
        onDoubleClicked: {
            root.min_max()
        }

        // This is the important part:
        // If you don't do this, MouseArea might swallow all clicks
        onClicked: (mouse) => {
            mouse.accepted = false
        }
    }
}
