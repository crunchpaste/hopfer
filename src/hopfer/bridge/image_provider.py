from PySide6.QtQuick import QQuickImageProvider
from PySide6.QtCore import Signal
from PySide6.QtGui import QImage


class ImageProvider(QQuickImageProvider):
    imageChanged = Signal()

    def __init__(self):
        super().__init__(QQuickImageProvider.Image)
        self.image = QImage()

    def setImage(self, image):
        self.image = image
        self.imageChanged.emit()

    def requestImage(self, id, size, requestedSize):
        if self.image.isNull():
            placeholder = QImage(100, 100, QImage.Format_RGB32)
            placeholder.fill(0xFF000000)  # black
            return placeholder
        return self.image
