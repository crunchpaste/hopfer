import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ComboBox {
    id: root
    popup: Popup {

       y: 0

       id: comboPopup

       width: root.width * config.window.ui_scale

       height: Math.min((list.implicitHeight + 10) * config.window.ui_scale, root.Window.height - 50)
       padding: 0
       contentItem: Item{
           width: comboPopup.height / config.window.ui_scale
           height: comboPopup.height / config.window.ui_scale
           transform: Scale {
               xScale: config.window.ui_scale
               yScale: config.window.ui_scale
               origin.x: 0; origin.y: 0
           }
           ListView {
               id: list
               clip: true
               implicitHeight: contentHeight
               width: parent.width / config.window.ui_scale
               height: parent.height / config.window.ui_scale
               topMargin: 5
               bottomMargin: 5
               model: root.popup.visible ? root.delegateModel : null
               currentIndex: root.highlightedIndex
               ScrollIndicator.vertical: ScrollIndicator { }
           }
       }
       // keeping it in case i decide to match the ones in the halftone and image tabs
       // background: Rectangle {
       //
       //     color: Material.background
       //
       //     border.color: Material.accent
       //
       //     border.width: 2
       //
       //     radius: 5
       // }
   }
}
