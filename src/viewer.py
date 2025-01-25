from PySide6 import QtCore, QtGui, QtWidgets
from viewer_controls import ViewerControls

class PhotoViewer(QtWidgets.QGraphicsView):
    """Quite literally taken from ekhumoro's answer at https://stackoverflow.com/questions/35508711/how-to-enable-pan-and-zoom-in-a-qgraphicsview. It's not perfect and glitches every once in a while, but it gets the job done for now.
    """
    coordinatesChanged = QtCore.Signal(QtCore.QPoint)

    SCALE_FACTOR = 1.25  # Class-level constant for scaling factor

    def __init__(self, parent=None):
        super().__init__(parent)
        self._zoom = 0
        self._pinned = False
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()

        self._photo.setTransformationMode(QtCore.Qt.TransformationMode.FastTransformation)
        self._photo.setShapeMode(QtWidgets.QGraphicsPixmapItem.ShapeMode.BoundingRectShape)
        self._blur = QtWidgets.QGraphicsBlurEffect()
        self._blur.setBlurHints(QtWidgets.QGraphicsBlurEffect.PerformanceHint)
        self._blur.setBlurRadius(1.1)
        self._blur.setEnabled(False)
        self._photo.setGraphicsEffect(self._blur)
        self._scene.addItem(self._photo)
        self.setScene(self._scene)

        self.setTransformationAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(34, 35, 35, 0)))
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

        self.controls = ViewerControls(self)

        # Connect the button event for the controller class
        self.controls.fit.clicked.connect(self.resetView)
        self.controls.x1.clicked.connect(self.resetOriginal)
        self.controls.x2.clicked.connect(lambda: self.resetToScale(scale=2))
        self.controls.blur.clicked.connect(
            lambda: self._blur.setEnabled(not self._blur.isEnabled()))

    def hasValidPhoto(self):
        """Check if the viewer currently has a valid photo."""
        return not self._empty

    def setPhoto(self, pixmap=None):
        """Set a new photo in the viewer."""
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(34, 35, 35)))
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())

    def resetView(self, scale=1):
        """Reset the view to fit the photo within the viewport."""
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            scale = max(1, scale)  # Ensure scale is at least 1
            if self.hasValidPhoto():
                self._scaleToFit(rect, scale)
                self.centerOn(self._photo)
                self.updateCoordinates()
                self._zoom = 1

    def resetOriginal(self):
        """Reset the view to display the photo at its original size."""
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            self.resetTransform()
            self.setTransform(QtGui.QTransform())
            self.centerOn(self._photo)

            self.updateCoordinates()

    def resetToScale(self, scale=1):
        """Reset the view to display the photo at an arbitrary scale."""
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            scale = max(1, scale)  # Ensure scale is at least 1
            if self.hasValidPhoto():
                # Apply the custom scale factor
                self.setTransform(QtGui.QTransform())  # Reset any previous transformations
                self.scale(scale, scale)  # Apply custom scale factor
                self.centerOn(self._photo)

                self.updateCoordinates()
                self._photo.setTransformationMode(QtCore.Qt.TransformationMode.FastTransformation)

    def _scaleToFit(self, rect, scale):
        """Helper method to scale the photo to fit the viewport."""
        unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
        self.scale(1 / unity.width(), 1 / unity.height())
        viewrect = self.viewport().rect()
        scenerect = self.transform().mapRect(rect)
        factor = min(viewrect.width() / scenerect.width(),
                     viewrect.height() / scenerect.height()) * scale
        self.scale(factor, factor)

    def zoom(self, step):
        """Zoom in or out based on the step value."""
        zoom = max(0, self._zoom + int(step))
        if zoom != self._zoom:
            self._zoom = zoom
            factor = self.SCALE_FACTOR ** abs(step) if step > 0 else 1 / (self.SCALE_FACTOR ** abs(step))
            self.scale(factor, factor) if self._zoom > 0 else self.resetView()

        # Get the bounding rectangle of the photo
        rect = self._photo.boundingRect()
        # Apply the current transformation matrix to the rectangle
        transformed_rect = self.transform().mapRect(rect)

        # print(rect, "\n", transformed_rect)

        if rect.width() > transformed_rect.width() / 2:
            self._photo.setTransformationMode(QtCore.Qt.TransformationMode.SmoothTransformation)
        else:
            self._photo.setTransformationMode(QtCore.Qt.TransformationMode.FastTransformation)

    def wheelEvent(self, event):
        """Handle zooming via mouse wheel."""
        delta = event.angleDelta().y()
        self.zoom(delta // abs(delta) if delta else 0)

    def resizeEvent(self, event):
        """Reset the view when the widget is resized."""
        super().resizeEvent(event)
        self.resetView()
        # Get the size of the viewer
        viewer_width = self.width()
        viewer_height = self.height()

        # Get the dimensions of the controls widget
        controls_width = 300#self.controls.width()
        controls_height = 64 #self.controls.height()

        # Position the controls widget in the top-right corner
        x = viewer_width - controls_width - 5 # 10px padding from the right
        y = viewer_height - controls_height # 10px padding from the top
        self.controls.setGeometry(x, y, controls_width, controls_height)

    def toggleDragMode(self):
        """Toggle between scroll hand drag mode and no drag mode."""
        if self.dragMode() == QtWidgets.QGraphicsView.DragMode.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)

    def updateCoordinates(self, pos=None):
        """Emit the updated coordinates of the mouse relative to the photo."""
        if self._photo.isUnderMouse():
            pos = pos or self.mapFromGlobal(QtGui.QCursor.pos())
            point = self.mapToScene(pos).toPoint()
        else:
            point = QtCore.QPoint()
        self.coordinatesChanged.emit(point)

    def mouseMoveEvent(self, event):
        """Track mouse movement for coordinate updates."""
        self.updateCoordinates(event.position().toPoint())
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        """Handle mouse leave event."""
        self.coordinatesChanged.emit(QtCore.QPoint())
        super().leaveEvent(event)
