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

    x: config.window.x
    y: config.window.y
    width: config.window.width
    height: config.window.height

    minimumWidth: 850
    minimumHeight: 650

    visibility: config.window.maximized ? Window.Maximized : Window.Windowed


    title: "hopfer"

    property bool isNative: config.window.native_frame
    property bool themeIdx: config.style.theme

    // used for the config
    property int accent: theme.selectedIndex
    property bool maximized: visibility == Window.Maximized
    // this is the sidebar width
    property alias sbw: sidebar.width

    flags: isNative ? Qt.Window : Qt.Window | Qt.FramelessWindowHint
    font.family: "Jetbrains Mono"
    font.pointSize: config.style.font_size
    Material.theme: themeIdx == 0 ? Material.Dark : Material.Light
    Material.roundedScale: Material.ExtraSmallScale
    Material.containerStyle: Material.Outlined

    ThemeManager {
        id: theme
        dark: main_window.themeIdx == 0
        selectedIndex: config.style.accent
    }


    Material.accent: theme.currentAccent

    Shortcut {
      sequence: StandardKey.Open
      onActivated: {
        openDialog.open();
      }
    }
    Shortcut {
      sequence: StandardKey.Save
      onActivated: {
        if (viewer.hasImage) {
          bridge.save(saveDialog.selectedFile);
        }
      }
    }
    Shortcut {
      sequence: StandardKey.SaveAs
      onActivated: {
        if (viewer.hasImage) {
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
    Connections {
        function onDisplayImage() {
            viewer.source = "image://preview/current?" + Date.now();
            busy_timer.stop();
            viewer.busy(false);
        }

        function onEnableToolbar(state) {
            toolbar.enable_toolbar(state);
        }

        function onOriginalGrayscale(state) {
            image_panel.grascale_enabled = !state;
        }

        function onResetView() {
            viewer.fit();
        }

        function onProcessingStarted() {
            busy_timer.restart();
        }

        function onLoadFailed() {
            busy_timer.stop();
            viewer.busy(false);
            console.log("failed");
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

    FileDialog {
        // TODO: Update the path even when image was dropped or pasted
        id: openDialog

        property url lastFolder: StandardPaths.writableLocation(StandardPaths.PicturesLocation)

        fileMode: FileDialog.OpenFile
        modality: Qt.WindowModal
        currentFolder: StandardPaths.writableLocation(StandardPaths.PicturesLocation)
        Component.onCompleted: {
            if (config.paths.open_path !== "") {
                currentFolder = Qt.resolvedUrl("file:///" + config.paths.open_path);
                lastFolder = currentFolder;
            }
        }
        nameFilters: [
            "Image files (*.png *.PNG *.jpg *.JPG *.jpeg *.JPEG *.tiff *.TIFF *.tif *.TIF *.webp *.WEBP *.gif *.GIF)",
            "All files (*)"
        ]
        onAccepted: {
            bridge.open(selectedFile);
            currentFolder = selectedFile;
            lastFolder = currentFolder;
            let openPath = selectedFile.toString();
            lastFolder = openPath.substring(0, openPath.lastIndexOf("/"));
            // in case the user has already saved a file to a folder, just change the fileName otherwise replace the whole taget folder
            if (saveDialog.modified) {
                let fileName = openPath.substring(openPath.lastIndexOf("/") + 1);
                let saveFolder = saveDialog.currentFolder.toString();
                if (!saveFolder.endsWith("/")) {
                    saveFolder += "/";
                }
                Qt.callLater(() => {
                    saveDialog.selectedFile = Qt.resolvedUrl(saveFolder + fileName);
                });
            } else {
                Qt.callLater(() => {
                    saveDialog.selectedFile = selectedFile;
                });
            }
        }
        onRejected: {
            currentFolder = lastFolder;
        }
    }

    FileDialog {
        id: saveDialog

        property url lastFolder: StandardPaths.writableLocation(StandardPaths.PicturesLocation)
        property bool modified: false

        // title: "Save image as"
        fileMode: FileDialog.SaveFile
        options: FileDialog.DontConfirmOverwrite
        modality: Qt.WindowModal
        defaultSuffix: "png"
        currentFolder: StandardPaths.writableLocation(StandardPaths.PicturesLocation)
        selectedFile: currentFolder + "/hopfer.png"
        Component.onCompleted: {
            if (config.paths.save_path !== "") {
                currentFolder = Qt.resolvedUrl("file:///" + config.paths.open_path);
            }
        }
        nameFilters: [
            "PNG files (*.png. *.PNG)",
            "TIFF files (*.tif *.tiff *.TIF *.TIFF)",
            "All files (*)"]

        onAccepted: {
            bridge.save(selectedFile);
            currentFolder = selectedFile;
            lastFolder = currentFolder;
            modified = true;
        }
        onRejected: {
            currentFolder = lastFolder;
        }
    }

    PreferencesDialog {
        id: preferences
        modality: Qt.WindowModal
        darkTheme: main_window.themeIdx == 0
        accent: main_window.accent

        onToggleTheme: state => {
            main_window.themeIdx = state ? 0 : 1;
            raise();
        }
        onAccentSelected: index => {
            theme.selectedIndex = index;
        }
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
                // width: main_window.width
                Layout.fillWidth: true
                visible: !main_window.isNative
            }

            SplitView {
                Layout.fillWidth: true
                Layout.fillHeight: true

                Item {
                    id: sidebar
                    SplitView.minimumWidth: 400
                    SplitView.preferredWidth: config.window.sidebar_width
                    SplitView.fillHeight: true

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
                            onOpenPreferences: {
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
                            // anchors.centerIn: parent
                            fill: Material.foreground
                            Layout.leftMargin: 10
                            opacity: viewer.hasImage ? 0 : 0.05
                        }

                        Label {
                            text: "Open image or drop files here"
                            // anchors.fill: parent
                            // anchors.horizontalCenter: parent.horizontalCenter
                            // anchors.bottomMargin: 50
                            // anchors.bottom: parent.bottom
                            opacity: viewer.hasImage ? 0 : 0.15
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

        // CORNERS (drawn last = higher stacking)
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
