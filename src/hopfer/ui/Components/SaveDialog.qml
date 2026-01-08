import QtQuick
import QtCore
import QtQuick.Controls
import QtQuick.Dialogs

FileDialog {
    id: control

    property url lastFolder: StandardPaths.writableLocation(StandardPaths.PicturesLocation)
    property bool modified: false

    fileMode: FileDialog.SaveFile
    options: FileDialog.DontConfirmOverwrite
    modality: Qt.WindowModal
    defaultSuffix: "png"
    currentFolder: StandardPaths.writableLocation(StandardPaths.PicturesLocation)
    selectedFile: currentFolder + "/hopfer.png"

    Component.onCompleted: {
        if (config.paths.save_path !== "") {
            currentFolder = Qt.resolvedUrl(fixPath(config.paths.save_path));
        }
    }

    nameFilters: [
        "PNG files (*.png. *.PNG)",
        "TIFF files (*.tif *.tiff *.TIF *.TIFF)",
        "All files (*)"
    ]

    function fixPath(p) {
        if (p === "") return StandardPaths.writableLocation(StandardPaths.PicturesLocation);
        return (p.indexOf(":") !== -1 && p.indexOf("file://") === -1) ? "file:///" + p : p;
    }

    function syncName(openPathUrl) {
        let openPath = openPathUrl.toString();
        let fileName = openPath.substring(openPath.lastIndexOf("/") + 1);

        if (modified) {
            let saveFolder = currentFolder.toString();
            if (!saveFolder.endsWith("/")) saveFolder += "/";

            Qt.callLater(() => {
                selectedFile = Qt.resolvedUrl(saveFolder + fileName);
            });
        } else {
            Qt.callLater(() => {
                selectedFile = openPathUrl;
            });
        }
    }

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
