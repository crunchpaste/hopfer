import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

Item {
    id: root

    ScrollView {
        id: scrollRoot
        anchors.fill: parent

        contentWidth: -1
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
        ScrollBar.vertical.policy: ScrollBar.AlwaysOff

        ListModel {
            id: generalShortcuts
            ListElement { name: "Open image"; seq: "Ctrl+O" }
            ListElement { name: "Save image"; seq: "Ctrl+S" }
            ListElement { name: "Save as"; seq: "Shift+Ctrl+S" }
            ListElement { name: "Copy to clipboard"; seq: "Ctrl+C" }
            ListElement { name: "Paste from clipboard"; seq: "Ctrl+V" }
            // ListElement { name: "Preferences dialog"; seq: "Ctrl+P" }
            ListElement { name: "Close app"; seq: "Ctrl+Q" }
        }

        ListModel {
            id: viewerShortcuts
            ListElement { name: "Fit to viewbox"; seq: "Ctrl+0" }
            ListElement { name: "Zoom level"; seq: "Ctrl+1-9" }
        }

        ListModel {
            id: imageShortcuts
            ListElement { name: "Jump to image tab"; seq: "Ctrl+I" }
            ListElement { name: "Jump to halftone tab"; seq: "Ctrl+H" }
            ListElement { name: "Jump to output tab"; seq: "Ctrl+E" }
            ListElement { name: "Resize image"; seq: "Shift+Ctrl+I" }
            ListElement { name: "Invert image"; seq: "Shift+Ctrl+N" }
            ListElement { name: "Rotate image CW"; seq: "Ctrl+R" }
            ListElement { name: "Rotate image CCW"; seq: "Shift+Ctrl+R" }
            ListElement { name: "Flip image"; seq: "Ctrl+F" }
        }

        ColumnLayout {
            width: scrollRoot.availableWidth
            spacing: 0

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
                        text: "General"
                        font.bold: true
                        font.pointSize: 10
                        color: Material.accent
                        Layout.bottomMargin: 5
                        opacity: 0.75
                    }

                    Repeater {
                        model: generalShortcuts
                        delegate: ShortcutRow {
                            Layout.fillWidth: true
                            label: name
                            sequence: seq
                        }
                    }
                }
            }

            Pane {
                Layout.fillWidth: true
                Layout.margins: 20
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
                        text: "Viewer"
                        font.bold: true
                        font.pointSize: 10
                        color: Material.accent
                        Layout.bottomMargin: 5
                        opacity: 0.75
                    }

                    Repeater {
                        model: viewerShortcuts
                        delegate: ShortcutRow {
                            Layout.fillWidth: true
                            label: name
                            sequence: seq
                        }
                    }
                }
            }

            Pane {
                Layout.fillWidth: true
                Layout.margins: 20
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
                        text: "Image processing"
                        font.bold: true
                        font.pointSize: 10
                        color: Material.accent
                        Layout.bottomMargin: 5
                        opacity: 0.75
                    }

                    Repeater {
                        model: imageShortcuts
                        delegate: ShortcutRow {
                            Layout.fillWidth: true
                            label: name
                            sequence: seq
                        }
                    }
                }
            }

            Item { Layout.fillHeight: true }
        }
    }
}
