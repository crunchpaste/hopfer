import Components
import Icons
import QtCore
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

ApplicationWindow {
    id: root

    title: "Preferences"
    width: Math.floor(520 * config.window.ui_scale)
    height: Math.floor(790 * config.window.ui_scale)

    font.family: "Jetbrains Mono"
    font.pointSize: 11

    minimumWidth: width
    maximumWidth: width
    minimumHeight: height
    maximumHeight: height

    function center() {
        let mwx = config.window.x
        let mwy = config.window.y
        let mww = config.window.width
        let mwh = config.window.height
        x = mwx + (mww - width) / 2
        y = mwy + (mwh - height) / 2
    }
    onVisibleChanged: {
        if (visible) center()
    }

    // cant be bothered to make the shadows work on windows so non-system frame is disabled permanently
    property int isNative: (Qt.platform.os === "windows") ? 0 : config.window.native_frame
    property alias currentIndex: bar.currentIndex

    flags: isNative ? Qt.Window : Qt.FramelessWindowHint | Qt.SubWindow
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
            visible: !root.isNative
            window: root
            title: "Preferences"
            Layout.fillWidth: true
            Layout.preferredHeight: 45
        }

        ScaleContainer {
            zoom: config.window.ui_scale
            Layout.fillWidth: true
            Layout.fillHeight: true
            ColumnLayout{
              anchors.fill: parent
              TitlebarIcon {
                id: logo
                Layout.preferredHeight: 150
                Layout.preferredWidth: height * (81 / 40)

                Layout.alignment: Qt.AlignHCenter

                fill: Material.foreground
                opacity: 0.9
              }
              Label {
                text: `v${config.version}`
                Layout.alignment: Qt.AlignHCenter
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
                Layout.margins: 0
                PreferencesTab {}
                ShortcutTab {}
                AboutTab {}
              }
            }
        }
    }
}
