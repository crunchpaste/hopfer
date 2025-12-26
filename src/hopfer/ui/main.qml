// import QtQuick.Controls.Basic
import Components
import QtCore
import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Dialogs
import QtQuick.Layouts
import QtQuick.Shapes
import QtQuick.VectorImage
import Settings

ApplicationWindow {
    id: main_window
    visible: true
    height: 800
    width: 1200
    minimumWidth: 850
    minimumHeight: 600

    title: "hopfer"

    // property bool native: false
    property bool isNative: false
    property bool darkTheme: true

    // readonly property color adaptiveColor: (Material.theme === Material.Dark) ? "ghostwhite" : "#393d47"

    flags: isNative ? Qt.Window : Qt.Window | Qt.FramelessWindowHint
    font.family: "Jetbrains Mono"
    font.pointSize: 11
    Material.theme: darkTheme ? Material.Dark : Material.Light
    Material.roundedScale: Material.ExtraSmallScale
    Material.containerStyle: Material.Outlined

    Shortcut {
        sequence: StandardKey.Open
        onActivated: {
            openDialog.open();
        }
    }

    ThemeManager {
        id: theme
        dark: main_window.darkTheme
    }

    Material.accent: theme.currentAccent
    // Material.background: theme.windowBg

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
        }

        function onShowNotification(message, duration) {
            snack.show(message, duration);
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
        id: openDialog

        property url lastFolder: StandardPaths.writableLocation(StandardPaths.PicturesLocation)

        fileMode: FileDialog.OpenFile
        modality: Qt.WindowModal
        currentFolder: StandardPaths.writableLocation(StandardPaths.PicturesLocation)
        Component.onCompleted: {
            if (bridge.initial_folder_url !== "") {
                currentFolder = bridge.initial_folder_url;
                lastFolder = currentFolder;
            }
        }
        nameFilters: ["Image files (*.png *.jpg *.jpeg *.tiff, *.tif, *.webp, *.gif)", "All files (*)"]
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

                saveDialog.selectedFile = Qt.resolvedUrl(saveFolder + fileName);
            } else {
                saveDialog.selectedFile = selectedFile;
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
        currentFile: "hopfer.png"
        Component.onCompleted: {
            if (bridge.initial_folder_url !== "") {
                currentFolder = bridge.initial_folder_url;
            }
        }
        nameFilters: ["PNG files (*.png)", "TIFF files (*.tif *.tiff)", "All files (*)"]

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
        isNative: main_window.isNative
        darkTheme: main_window.darkTheme
        onToggleNative: state => {
            main_window.isNative = state;
            raise();
        }
        onToggleTheme: state => {
            main_window.darkTheme = state;
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
                    SplitView.minimumWidth: 400
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
                            onActual: viewer.actual()
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

                    BackgroundLogo {
                        anchors.centerIn: parent
                        fill: Material.foreground
                        opacity: viewer.hasImage ? 0 : 0.05
                    }

                    SnackBar {
                        id: snack
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.bottom: parent.bottom
                        anchors.bottomMargin: 46
                        z: 100
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
