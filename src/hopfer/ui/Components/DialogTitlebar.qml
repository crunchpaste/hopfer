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
    required property Window window
    property alias title: label.text
    opacity: window.active ? 1.0 : 0.5
    width: parent.width
    height: 45
    layer.enabled: true
    layer.effect: MultiEffect {
        shadowEnabled: true
        shadowColor: "black"
        shadowBlur: 0.4      // How soft the shadow is
        shadowVerticalOffset: 3  // Moves the shadow down
        shadowOpacity: 0.3
    }
    function min_max() {
      if (window.visibility === Window.Maximized)
      window.showNormal()
      else
      window.showMaximized()
    }

    RowLayout {
        anchors.fill: parent
        anchors.leftMargin: 15
        anchors.rightMargin: 10
        Label {
            id: label
            font.family: "Jetbrains Mono"
            font.pointSize: 11
        }
        Item { Layout.fillWidth: true }
        TitlebarButton {
            icon: Component {Close{}}
            onClicked: window.close()
        }

    }

    DragHandler {
        target: null
        onActiveChanged: if (active) window.startSystemMove()
    }

    // Double click to maximize
    TapHandler {
        acceptedButtons: Qt.LeftButton
        onTapped: if (tapCount === 2) {
            root.min_max()
        }
    }

    // MouseArea{
    //     //deal with dragging
    //     anchors.fill: parent
    //     property variant clickPos: "1,1"
    //     onPressed: {
    //         if(window.visibility != 4 && window.visibility != 5)
    //             clickPos  = Qt.point(mouse.x,mouse.y)
    //     }
    //     onDoubleClicked: {
    //         var item = window.Maximized;
    //         if(window.visibility != 4 && window.visibility != 5){
    //             window.showMaximized()
    //         }
    //         else{
    //             window.showNormal()
    //         }
    //     }
    //
    //     onPositionChanged: {
    //         if(window.visibility != 4 && window.visibility != 5){
    //             var delta = Qt.point(mouse.x-clickPos.x, mouse.y-clickPos.y)
    //             window.x += delta.x;
    //             window.y += delta.y;
    //         }
    //     }
    // }
}
