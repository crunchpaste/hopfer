import QtQuick
import QtCore
import QtQuick.Controls
import QtQuick.Dialogs

FileDialog {
    id: control

    property var saveDialog: null

    property url lastFolder: StandardPaths.writableLocation(StandardPaths.PicturesLocation)

    fileMode: FileDialog.OpenFile
    modality: Qt.WindowModal
    currentFolder: StandardPaths.writableLocation(StandardPaths.PicturesLocation)

    Component.onCompleted: {
        if (config.paths.open_path !== "") {
            currentFolder = Qt.resolvedUrl(fixPath(config.paths.open_path));
            lastFolder = currentFolder;
        }
    }

    nameFilters: [
        "Image files (*.png *.PNG *.jpg *.JPG *.jpeg *.JPEG *.tiff *.TIFF *.tif *.TIF *.webp *.WEBP *.gif *.GIF)",
        "All files (*)"
    ]

    function fixPath(p) {
        if (p === "") return StandardPaths.writableLocation(StandardPaths.PicturesLocation);
        return (p.indexOf(":") !== -1 && p.indexOf("file://") === -1) ? "file:///" + p : p;
    }

    onAccepted: {
        bridge.open(selectedFile);

        // Update local folder state
        let openPath = selectedFile.toString();
        currentFolder = selectedFile;
        lastFolder = openPath.substring(0, openPath.lastIndexOf("/"));

        if (saveDialog) {
            saveDialog.syncName(selectedFile);
        }
    }

    onRejected: {
        currentFolder = lastFolder;
    }
}
