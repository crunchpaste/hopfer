import QtCore
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

DropArea {
    id: root
    signal droppedUrl(url url)

    onEntered: (drag) => {
        if (drag.hasUrls) {
            drag.accept(Qt.LinkAction);
            dropIndicator.visible = true;
        }
    }

    onExited: {dropIndicator.visible = false;}

    onDropped: (drop) => {
        if (drop.hasUrls) {
            let droppedUrl = drop.urls[0];
            drop.accept();
            root.droppedUrl(droppedUrl);
            dropIndicator.visible = false;
        }
    }

    Rectangle {
        id: dropIndicator
        anchors.fill: parent
        anchors.margins: 20

        radius: 10

        border.width: 3
        border.color: Qt.alpha(Material.accent, 0.5)
        color: Qt.alpha(Material.background, 0.7)
        z: 100

        visible: false

        ColumnLayout {
            id: dropLayout
            anchors.centerIn: parent
            spacing: 10

            Rectangle {
                color: Qt.alpha(Material.foreground, 0.1)
                width: 150
                height: 150
                radius: 75
                Layout.alignment: Qt.AlignHCenter

                Text {
                    anchors.centerIn: parent
                    text: "\ue2c6" // Material "Cloud Upload" or "File" icon code
                    font.family: "Material Icons"
                    font.pointSize: 48

                    color: Material.accent
                }
            }

            Item {
                height: 20
            }

            Label {
                text: "Upload file"
                font.bold: true
                font.pointSize: 14
                Layout.alignment: Qt.AlignHCenter
                color: "white"
            }

            Label {
                text: "Drop a file here to upload it."
                font.pointSize: 11
                opacity: 0.7
                Layout.alignment: Qt.AlignHCenter
                color: "white"
            }
        }
    }
}
