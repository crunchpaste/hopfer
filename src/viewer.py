from PySide6 import QtCore, QtGui, QtWidgets

from processing_label import ProcessingIndicator
from viewer_controls import ViewerControls


class PhotoViewer(QtWidgets.QGraphicsView):
    """Quite literally taken from ekhumoro's answer at https://stackoverflow.com/questions/35508711/how-to-enable-pan-and-zoom-in-a-qgraphicsview. It's not perfect and glitches every once in a while, but it gets the job done for now."""

    coordinatesChanged = QtCore.Signal(QtCore.QPoint)

    SCALE_FACTOR = 1.25  # Class-level constant for scaling factor

    def __init__(self, window, storage=None, parent=None):
        super().__init__(parent)

        self.setObjectName("viewer")

        self.window = window  # needed to regain focus after a drop
        self.colors = window.colors
        # self.storage = storage  # needed to load image after a drop
        self.setAcceptDrops(True)

        self._zoom = 0
        self._pinned = False
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()

        screen = QtWidgets.QApplication.primaryScreen()
        self.dpi_scaling = screen.devicePixelRatio()

        self._photo.setTransformationMode(
            QtCore.Qt.TransformationMode.FastTransformation
        )
        self._photo.setShapeMode(
            QtWidgets.QGraphicsPixmapItem.ShapeMode.BoundingRectShape
        )
        self._blur = QtWidgets.QGraphicsBlurEffect()
        self._blur.setBlurHints(QtWidgets.QGraphicsBlurEffect.PerformanceHint)
        self._blur.setBlurRadius(1.05)
        self._blur.setEnabled(False)
        self._photo.setGraphicsEffect(self._blur)
        self._scene.addItem(self._photo)
        self.setScene(self._scene)

        self.setTransformationAnchor(
            QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setResizeAnchor(
            QtWidgets.QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setVerticalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(34, 35, 35, 0)))
        self.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)

        self.label = ProcessingIndicator(self)
        self.label.show()
        self.label.setVisible(False)

        self.controls = ViewerControls(self)

        # Connect the button event for the controller class
        self.controls.fit.clicked.connect(self.resetView)
        self.controls.x1.clicked.connect(self.resetOriginal)
        self.controls.x2.clicked.connect(lambda: self.resetToScale(scale=2))
        self.controls.blur.clicked.connect(self.toggleBlur)

        self.set_theme()

    def hasValidPhoto(self):
        """Check if the viewer currently has a valid photo."""
        return not self._empty

    def setPhoto(self, pixmap=None):
        """Set a new photo in the viewer."""
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setBackgroundBrush(
                QtGui.QBrush(QtGui.QColor(self.colors.secondary))
            )
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        self.labelVisible(False)

    def toggleBlur(self):
        # Toggle the blur effect and apply a style to the button
        self._blur.setEnabled(not self._blur.isEnabled())
        self.blurBtnBG()

    def blurBtnBG(self):
        if self._blur.isEnabled():
            self.controls.blur.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.colors.primary};
                    color: {self.colors.secondary};
                }}
                QPushButton:hover {{
                    background-color: {self.colors.secondary};
                    color: {self.colors.primary};
                }}
            """)
        else:
            self.controls.blur.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.colors.secondary};
                    color: {self.colors.primary};
                }}
                QPushButton:hover {{
                background-color: {self.colors.primary};
                color: {self.colors.secondary};
                }}
            """)

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

            # in case the display is set at custom scaling
            # this should negate it. Mostly done as Windows defaults
            # to 125% scale and images look horrible.
            sf = 1 / self.dpi_scaling
            self.scale(sf, sf)

            self.centerOn(self._photo)

            self.updateCoordinates()

    def resetToScale(self, scale=1):
        """Reset the view to display the photo at an arbitrary scale."""
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            scale = max(1, scale)  # Ensure scale is at least 1
            if self.hasValidPhoto():
                self.setTransform(QtGui.QTransform())
                # in case the display is set at custom scaling
                # this should negate it. Mostly done as Windows defaults
                # to 125% scale and images look horrible.
                sf = 1 / self.dpi_scaling
                self.scale(scale * sf, scale * sf)  # Apply custom scale factor
                self.centerOn(self._photo)

                self.updateCoordinates()
                self._photo.setTransformationMode(
                    QtCore.Qt.TransformationMode.FastTransformation
                )

    def _scaleToFit(self, rect, scale):
        """Helper method to scale the photo to fit the viewport."""
        unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
        self.scale(1 / unity.width(), 1 / unity.height())
        viewrect = self.viewport().rect()
        scenerect = self.transform().mapRect(rect)
        factor = (
            min(
                viewrect.width() / scenerect.width(),
                viewrect.height() / scenerect.height(),
            )
            * scale
        )
        self.scale(factor, factor)

    def zoom(self, step):
        """Zoom in or out based on the step value."""
        zoom = max(0, self._zoom + int(step))
        if zoom != self._zoom:
            self._zoom = zoom
            factor = (
                self.SCALE_FACTOR ** abs(step)
                if step > 0
                else 1 / (self.SCALE_FACTOR ** abs(step))
            )
            self.scale(factor, factor) if self._zoom > 0 else self.resetView()

        # Get the bounding rectangle of the photo
        rect = self._photo.boundingRect()
        # Apply the current transformation matrix to the rectangle
        transformed_rect = self.transform().mapRect(rect)

        # print(rect, "\n", transformed_rect)

        if rect.width() > transformed_rect.width() / 2:
            self._photo.setTransformationMode(
                QtCore.Qt.TransformationMode.SmoothTransformation
            )
        else:
            self._photo.setTransformationMode(
                QtCore.Qt.TransformationMode.FastTransformation
            )

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

        controls_width = 300  # self.controls.width()
        controls_height = 64  # self.controls.height()

        label_width = self.label.width()
        label_height = self.label.height()

        # Position the controls widget in the bottom right corner
        x = (
            viewer_width - controls_width - 1
        )  # Don't really know how the padding works, it's kinda weird
        y = viewer_height - controls_height + 4  # Vertically yoo
        self.controls.setGeometry(x, y, controls_width, controls_height)

        x = viewer_width // 2 - label_width // 2
        y = viewer_height // 2 - label_height // 2
        self.label.setGeometry(x, y, label_width, label_height)

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

    def mousePressEvent(self, event):
        self.window.titleBar.focus.setFocus()
        self.clearFocus()
        super().mousePressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()
            self.toggle_drop_border(True)

        else:
            print("Ignoring drag event (unknown format)")

    def dragMoveEvent(self, event):
        # Drops are not accepted if dragMoveEvent is not accepted for
        # some reason
        event.acceptProposedAction()

    def dropEvent(self, event):
        # remove the border as soon as possible
        self.toggle_drop_border(False)

        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.window.writer.load_image(file_path)
            self.window.get_focus()
            return

        text = event.mimeData().text().strip()
        if text.startswith("file://"):
            file_path = text[7:]  # Strip file://
            # self.storage.load_image(file_path)
            self.window.get_focus()

    def dragLeaveEvent(self, event):
        self.toggle_drop_border(False)

    def labelVisible(self, state):
        self.label.setVisible(state)

    def toggle_drop_border(self, show):
        # A border that indicates if a file could be dropped
        if show:
            self.setStyleSheet("QGraphicsView {border: 2px solid salmon}")
        else:
            # a transparent 2px border is being used so that the resize
            # event is not triggered as it is quite jarring. The border is
            # compensated with the margin in style.css
            self.setStyleSheet("QGraphicsView {border: 2px solid transparent}")

    def set_theme(self):
        if self.hasValidPhoto():
            self.setBackgroundBrush(
                QtGui.QBrush(QtGui.QColor(self.colors.secondary))
            )
        self.blurBtnBG()

    def reset_to_default(self):
        # removes image and resets everything to defaults
        self._photo.setPixmap(QtGui.QPixmap())  # Clear the image
        self._empty = True
        self._zoom = 0

        self.resetTransform()
        self.setTransform(QtGui.QTransform())
        self._photo.setTransformationMode(
            QtCore.Qt.TransformationMode.FastTransformation
        )

        self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(34, 35, 35, 0)))

        self.setSceneRect(QtCore.QRectF())

        self.update()
