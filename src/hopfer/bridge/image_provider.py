import logging

import numpy as np
from PySide6.QtCore import Signal
from PySide6.QtGui import QImage
from PySide6.QtQuick import QQuickImageProvider

logger = logging.getLogger(__name__)


class ImageProvider(QQuickImageProvider):
    imageChanged = Signal()

    def __init__(self):
        super().__init__(QQuickImageProvider.Image)
        self.image = QImage()

    def setImage(self, array_slice, is_rgb=False):
        """
        Expects a numpy array/slice.
        Handles pointer-based QImage creation and soft-blending.
        """
        if array_slice is None:
            return

        # QImage data must be contignous
        data = np.ascontiguousarray(array_slice)
        # get the shape
        h, w = data.shape[:2]
        # get the strides
        bytes_per_line = data.strides[0]

        # get the format
        if is_rgb:
            q_format = QImage.Format.Format_RGB888
        else:
            q_format = QImage.Format.Format_Grayscale8

        # construct the data from the pointer.
        # TODO: I believe this could be done even more efficiently, still, its much better than it was.
        qimg = QImage(data.data, w, h, bytes_per_line, q_format)

        self.image = qimg
        self.imageChanged.emit()

    def closeImage(self):
        # remove the reference to the image so that multiprocessing does not compalin about existing pointers
        logger.debug("Closing image pointer in ImageProvider")
        self.image = QImage()
        self.imageChanged.emit()

    def requestImage(self, id, size, requestedSize):
        if self.image.isNull():
            placeholder = QImage(100, 100, QImage.Format_RGB32)
            placeholder.fill(0xFF000000)  # black
            return placeholder
        return self.image
