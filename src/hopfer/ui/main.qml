import Components
import Icons
import QtCore
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Dialogs
import QtQuick.Layouts

ApplicationWindow {
    id: main_window
    visible: true

    title: "hopfer"

    x: config.window.x
    y: config.window.y
    // update them in the config
    onXChanged: config.window.x = x
    onYChanged: config.window.y = y

    width: config.window.width
    height: config.window.height
    // update them in the config
    onWidthChanged: config.window.width = width
    onHeightChanged: config.window.height = height

    minimumWidth: 850
    minimumHeight: 650

    visibility: {
        if (config.window.maximized) return Window.Maximized
        return Window.Windowed
    }
    // update it in the config
    onVisibilityChanged: (visibiity) => {
        if (visibility === Window.Maximized) {
            config.window.maximized = true
        } else if (visibility === Window.Windowed) {
            config.window.maximized = false
        }
    }

    // cant be bothered to make the shadows work on windows so non-system frame is disabled permanently
    property int isNative: (Qt.platform.os === "windows") ? 0 : config.window.native_frame
    property bool themeIdx: config.style.theme

    // Theme related

    ThemeManager {
        id: theme
        dark: main_window.themeIdx == 0
        selectedIndex: config.style.accent
    }

    flags: isNative ? Qt.Window : Qt.Window | Qt.FramelessWindowHint
    font.family: "Jetbrains Mono"
    font.pointSize: config.style.font_size
    Material.theme: themeIdx == 0 ? Material.Dark : Material.Light
    Material.roundedScale: Material.ExtraSmallScale
    Material.containerStyle: Material.Outlined
    Material.accent: theme.currentAccent

    // Shortcut related

    Shortcuts {
        openDialog: openDialog
        saveDialog: saveDialog
        tabBar: bar
        viewer: viewer
        toolbar: toolbar
    }

    // Bridge connection

    Connections {
        function onDisplayImage() {
            viewer.source = "image://preview/current?" + Date.now();
            busy_timer.stop();
            viewer.busy(false);
        }

        function onRemoveImage() {
            viewer.source = ""
            busy_timer.stop();
            viewer.busy(false);
        }

        function onOriginalGrayscale(state) {
            image_panel.grascale_enabled = !state;
        }

        function onResetView() {
            viewer.fit();
        }

        function onFileReceived(url) {
            openDialog.selectedFile = url
            saveDialog.syncName(url)
        }

        function onProcessingStarted() {
            busy_timer.restart();
        }

        function onLoadFailed() {
            busy_timer.stop();
            viewer.busy(false);
        }

        function onShowNotification(msg, duration) {
            snack.show(msg, duration);
        }

        target: bridge
    }

    Timer {
        id: busy_timer
        interval: 300
        repeat: false
        onTriggered: viewer.busy(true)
    }

    SaveDialog {
        id: saveDialog
    }

    OpenDialog {
        id: openDialog
        saveDialog: saveDialog
    }

    PreferencesDialog {
        id: preferences
        modality: Qt.WindowModal
    }

    Rectangle {
        anchors.fill: parent
        color: Material.background
        ColumnLayout {
            anchors.fill: parent
            spacing: 0

            Titlebar {
                id: tb
                z: 5
                app_window: main_window
                Layout.fillWidth: true
                visible: !main_window.isNative
            }
            ScaleContainer {
                zoom: config.window.ui_scale
                Layout.fillWidth: true
                Layout.fillHeight: true
                SplitView {
                    anchors.fill: parent

                    Item {
                        id: sidebar
                        SplitView.minimumWidth: 400
                        SplitView.preferredWidth: config.window.sidebar_width
                        SplitView.fillHeight: true
                        onWidthChanged: {
                          // when instantiated the sidebar is assigned it's minimum width. if we dont ignore this assignment it is never updated properly.
                          if (width != SplitView.minimumWidth) {
                            config.window.sidebar_width = width
                          }
                        }

                        RowLayout {
                            anchors.fill: parent
                            spacing: 0

                            Toolbar {
                                id: toolbar

                                Layout.fillHeight: true
                                onOpenClicked: openDialog.open()
                                onSaveAsClicked: saveDialog.open()
                                onSaveClicked: bridge.save(saveDialog.selectedFile)
                                onFitImage: viewer.fit()
                                onActual: viewer.to_scale(1)
                                onOpenShortcutOverlay: shortcutOverlay.open()
                                onOpenPreferences: (index) => {
                                    // preferences.currentIndex = index
                                    preferences.show();
                                    preferences.raise();
                                }
                            }

                            ColumnLayout {
                                TabBar {
                                    id: bar
                                    currentIndex: stack.currentIndex
                                    topPadding: 10

                                    Layout.fillWidth: true

                                    TabButton {
                                        text: "Image"
                                    }

                                    TabButton {
                                        text: "Halftone"
                                    }

                                    TabButton {
                                        text: "Output"
                                    }
                                }
                                StackLayout {
                                    id: stack
                                    currentIndex: bar.currentIndex

                                    Layout.fillWidth: true
                                    Layout.fillHeight: true
                                    Layout.margins: 20

                                    ImagePanel {
                                        id: image_panel
                                        onGrayscaleChanged: function (algorithm, settings) {
                                            let settings_json = JSON.stringify(settings);
                                            bridge.send_grayscale(algorithm, settings_json);
                                        }
                                        onEnhanceChanged: function (settings) {
                                            let settings_json = JSON.stringify(settings);
                                            bridge.send_enhance(settings_json);
                                        }
                                    }
                                    // Item {}

                                    HalftonePanel {
                                        id: halftone_panel
                                        onHalftoneChanged: function (algorithm, settings) {
                                            let settings_json = JSON.stringify(settings);
                                            bridge.send_halftone(algorithm, settings_json);
                                        }
                                    }
                                    OutputPanel {
                                        onColorsChanged: function (settings) {
                                            let settings_json = JSON.stringify(settings);
                                            bridge.send_colors(settings_json);
                                        }
                                    }
                                }
                            }
                        }
                    }

                    Viewer {
                        id: viewer

                        SplitView.fillHeight: true
                        SplitView.fillWidth: true
                        SplitView.minimumWidth: 400

                        ColumnLayout {
                            anchors.centerIn: parent
                            spacing: 30
                            Watermark {
                                fill: Material.foreground
                                Layout.leftMargin: 10
                                property real op: config.style.theme == 0 ? 0.05 : 0.1
                                opacity: bridge.has_image ? 0 : op
                            }

                            Label {
                                text: "Open image or drop files here"
                                property real op: config.style.theme == 0 ? 0.15 : 0.25
                                opacity: bridge.has_image ? 0 : op
                            }
                        }

                        SnackBar {
                            id: snack
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.bottom: parent.bottom
                            anchors.bottomMargin: 46
                            z: 100
                        }

                        Drop {
                            anchors.fill: parent
                            onDroppedUrl: url => {
                                bridge.open_url(url);
                                busy_timer.restart();
                            }
                        }
                    }
                }
            }
        }
    }

    Item {
        id: resizeContainer
        anchors.fill: parent
        z: 1000
        enabled: !main_window.isNative

        // TOP
        ResizeEdge {
            height: 6
            edge: Qt.TopEdge
            cursor: Qt.SizeVerCursor
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
        }

        // BOTTOM
        ResizeEdge {
            height: 6
            edge: Qt.BottomEdge
            cursor: Qt.SizeVerCursor
            anchors.bottom: parent.bottom
            anchors.left: parent.left
            anchors.right: parent.right
        }

        // LEFT
        ResizeEdge {
            width: 6
            edge: Qt.LeftEdge
            cursor: Qt.SizeHorCursor
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.bottom: parent.bottom
        }

        // RIGHT
        ResizeEdge {
            width: 6
            edge: Qt.RightEdge
            cursor: Qt.SizeHorCursor
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.bottom: parent.bottom
        }

        // CORNERS
        ResizeEdge {
            width: 10
            height: 10
            edge: Qt.TopEdge | Qt.LeftEdge
            cursor: Qt.SizeFDiagCursor
            anchors.top: parent.top
            anchors.left: parent.left
        }

        ResizeEdge {
            width: 10
            height: 10
            edge: Qt.TopEdge | Qt.RightEdge
            cursor: Qt.SizeBDiagCursor
            anchors.top: parent.top
            anchors.right: parent.right
        }

        ResizeEdge {
            width: 10
            height: 10
            edge: Qt.BottomEdge | Qt.LeftEdge
            cursor: Qt.SizeBDiagCursor
            anchors.bottom: parent.bottom
            anchors.left: parent.left
        }

        ResizeEdge {
            width: 10
            height: 10
            edge: Qt.BottomEdge | Qt.RightEdge
            cursor: Qt.SizeFDiagCursor
            anchors.bottom: parent.bottom
            anchors.right: parent.right
        }
    }

    component ResizeEdge: Item {
        required property int edge
        required property int cursor

        HoverHandler {
            cursorShape: parent.cursor
        }

        DragHandler {
            acceptedButtons: Qt.LeftButton
            grabPermissions: PointerHandler.CanTakeOverFromAnything
            onActiveChanged: {
                if (active) {
                    if (main_window.visibility === Window.Maximized)
                        return;
                    main_window.startSystemResize(parent.edge);
                }
            }
        }
    }
}
