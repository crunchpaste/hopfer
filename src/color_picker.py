import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsLineItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)
from qframelesswindow import FramelessDialog

from controls.slider_control import SliderControl
from controls.titlebar import DialogTitleBar
from helpers.load_stylesheet import load_qss
from res_loader import get_path


class ColorPicker(FramelessDialog):
    """
    This class is mostly created as Windows does not offer any color picker
    and a found the default Qt one rather bulky, clunky and quite frankly
    just a bit ugly.
    """

    def __init__(self, color=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Color Picker")
        self.setFixedSize(905, 600)
        outer_layout = QVBoxLayout(self)
        layout = QHBoxLayout()

        if color is None:
            self.color = QColor("salmon")
        else:
            self.color = color

        self.hsv = HSVWidget()
        self.hsv.hsv_changed.connect(self.update_rgb)

        self.controls = ColorControls(self.color)

        self.preview = self.controls.preview
        self.rgb_sliders = self.controls.sliders
        self.accept_button = self.controls.button
        self.rgb_sliders.rgb_changed.connect(self.update_hsv)

        self.accept_button.clicked.connect(self.accept)

        outer_layout.addSpacerItem(
            QSpacerItem(
                0, 45, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
            )
        )

        layout.addWidget(self.hsv)

        layout.addSpacerItem(
            QSpacerItem(
                15, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum
            )
        )

        layout.addWidget(self.controls)
        layout.addStretch()

        outer_layout.addLayout(layout)

        self.accept_button.setDefault(True)

        self.update_preview(self.color)
        self.update_rgb(self.color)
        self.update_hsv(self.color)

        self.setTitleBar(DialogTitleBar(self, label="Color picker"))
        self.titleBar.focus.setFocus()
        self.titleBar.raise_()

    def update_preview(self, color):
        self.color = color
        self.preview.update_color(color)

    def update_hsv(self, color):
        self.hsv.update_hsv(color)
        self.preview.update_color(color)

    def update_rgb(self, color):
        self.rgb_sliders.update_rgb(color)
        self.update_preview(color)

    def mousePressEvent(self, event):
        # resetting focus on click, just like the main window.
        super().mousePressEvent(event)
        self.titleBar.focus.setFocus()
        self.clearFocus()

    def pick_color(self):
        return self.color


class ColorControls(QWidget):
    # just a container for all of the controls
    def __init__(self, default, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setFixedHeight(510)

        self.preview = ColorPreview()
        self.sliders = RGBSliders(default)

        self.button = QPushButton("Accept")

        layout.addWidget(self.preview)
        layout.addWidget(self.sliders)
        layout.addStretch()
        layout.addWidget(self.button)

        self.setLayout(layout)


class ColorPreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(255, 255)

        self.label = QLabel(self)
        self.label.setFixedSize(255, 255)
        self.label.setStyleSheet("background-color: black;")

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        layout.setContentsMargins(0, 0, 0, 0)

    def update_color(self, color):
        # it may be somewhat primitive, but seemed a simple way of diplaying
        # the swatch
        self.label.setStyleSheet(f"background-color: {color.name()};")


class RGBSliders(QWidget):
    # Captured by the dialog
    rgb_changed = Signal(QColor)

    def __init__(self, default, parent=None):
        super().__init__(parent)

        self.r = default.red()
        self.g = default.green()
        self.b = default.blue()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.r_slider = SliderControl(
            "Red", (0, 255), self.r, False, stretch=True
        )
        self.g_slider = SliderControl(
            "Green", (0, 255), self.g, False, stretch=True
        )
        self.b_slider = SliderControl(
            "Blue", (0, 255), self.b, False, stretch=True
        )

        self.sliders = [self.r_slider, self.g_slider, self.b_slider]

        for slider in self.sliders:
            slider.value_changed.connect(self.on_rgb_change)
            layout.addWidget(slider)

        self.setFixedWidth(255)

        self.setLayout(layout)

    def update_rgb(self, color):
        r = color.red()
        g = color.green()
        b = color.blue()

        # Signals need to be blocked here, as RGB and HSV are not linear
        # therefore major glitching happens when near the SV square edges.
        self.r_slider.slider.blockSignals(True)
        self.g_slider.slider.blockSignals(True)
        self.b_slider.slider.blockSignals(True)

        self.r_slider.slider.setValue(r)
        self.g_slider.slider.setValue(g)
        self.b_slider.slider.setValue(b)

        # calling show reset manually as signals are disabled
        self.r_slider.show_reset(r)
        self.g_slider.show_reset(g)
        self.b_slider.show_reset(b)

        # calling the update value too
        self.r_slider.update_value(r)
        self.g_slider.update_value(g)
        self.b_slider.update_value(b)

        # Signals reneabled after the value of the sliders is set
        self.r_slider.slider.blockSignals(False)
        self.g_slider.slider.blockSignals(False)
        self.b_slider.slider.blockSignals(False)

    def on_rgb_change(self):
        self.r = self.r_slider.slider.value()
        self.g = self.g_slider.slider.value()
        self.b = self.b_slider.slider.value()

        color = QColor(self.r, self.g, self.b)

        self.rgb_changed.emit(color)


class HSVWidget(QWidget):
    hsv_changed = Signal(QColor)

    def __init__(self, hue=0, saturation=0, value=0, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()

        # Storage for the HSV values
        self.hue = hue
        self.saturation = 0
        self.value = 0

        self.h = HueWidget()
        self.sv = SaturationValueWidget()

        layout.addSpacerItem(
            QSpacerItem(
                0, 45, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
            )
        )

        self.h.h_changed.connect(self.on_hue_changed)
        self.sv.sv_changed.connect(self.on_sv_changed)
        layout.addWidget(self.h)
        layout.addSpacerItem(
            QSpacerItem(
                25, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum
            )
        )
        layout.addWidget(self.sv)

        self.setLayout(layout)

    def get_qcolor(self):
        color = QColor.fromHsv(self.hue, self.saturation, self.value)
        return color

    def on_hue_changed(self, hue):
        self.hue = hue
        self.sv.hue = hue
        self.sv.update_gradient()
        self.hsv_changed.emit(self.get_qcolor())

    def on_sv_changed(self, saturation, value):
        self.saturation = saturation
        self.value = value
        self.hsv_changed.emit(self.get_qcolor())

    def update_hsv(self, color):
        hue, saturation, value, _ = color.getHsv()
        self.hue = max(0, min(hue, 359))
        self.saturation = max(0, min(saturation, 255))
        self.value = max(0, min(value, 255))

        self.h.set_selection_from_hue(self.hue)
        self.sv.set_selection_from_hsv(self.hue, self.saturation, self.value)


class SaturationValueWidget(QGraphicsView):
    # Signal that the saturation/value has changed
    # captured by HSVWidget
    sv_changed = Signal(int, int)
    # Reset the stylesheet for now. should fix.
    style = """QGraphicsView {
        border: 0px;
        margin: 0px;
        min-width: 0px;
        background: transparent;
        }
    """

    def __init__(self, hue=0, size=510, parent=None):
        super().__init__(parent)

        self.setStyleSheet(self.style)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.hue = hue
        self.size = size
        self.setFixedSize(size, size)

        self._scene = QGraphicsScene(self)
        # set the viewbox
        self._scene.setSceneRect(0, 0, size, size)

        self._rect = QGraphicsRectItem(0, 0, size, size)
        self._rect.setPen(Qt.NoPen)

        self._scene.addItem(self._rect)

        self.setScene(self._scene)

        # the stroke of the crossheir
        self.crosshair_vline_o = QGraphicsLineItem(0, 0, 0, size)
        self.crosshair_hline_o = QGraphicsLineItem(0, 0, size, 0)
        self.crosshair_vline_o.setPen(QPen(QColor("#f0f6f0"), 3))
        self.crosshair_hline_o.setPen(QPen(QColor("#f0f6f0"), 3))

        # the line of the crossheir
        self.crosshair_vline_i = QGraphicsLineItem(0, 0, 0, size)
        self.crosshair_hline_i = QGraphicsLineItem(0, 0, size, 0)
        self.crosshair_vline_i.setPen(QPen(QColor("#222323"), 1))
        self.crosshair_hline_i.setPen(QPen(QColor("#222323"), 1))

        self._scene.addItem(self.crosshair_vline_o)  # Vertical stroke
        self._scene.addItem(self.crosshair_hline_o)  # Horizonral stroke
        self._scene.addItem(self.crosshair_vline_i)  # Vertical line
        self._scene.addItem(self.crosshair_hline_i)  # Horizonral line

        self.update_gradient()

    def update_gradient(self):
        # updates the hue. called both on slider change and hue change
        pixmap = self.generate_gradient(self.hue, self.size)
        self._rect.setBrush(QBrush(pixmap))

    @staticmethod
    def generate_gradient(hue, size):
        # this one traws the saturation/value gradient using two subsequent
        # linear gradients

        pixmap = QPixmap(size, size)
        painter = QPainter(pixmap)

        # saturation Gradient
        sat_gradient = QLinearGradient(0, 0, size, 0)
        sat_gradient.setColorAt(0, QColor(255, 255, 255))
        sat_gradient.setColorAt(1, QColor.fromHsv(hue, 255, 255))
        painter.fillRect(0, 0, size, size, sat_gradient)

        # value Gradient
        val_gradient = QLinearGradient(0, 0, 0, size)
        val_gradient.setColorAt(0, QColor(0, 0, 0, 0))
        val_gradient.setColorAt(1, QColor(0, 0, 0, 255))
        painter.fillRect(0, 0, size, size, val_gradient)

        painter.end()
        return pixmap

    def mousePressEvent(self, event):
        # these two handle the move and press of the mouse and trigger a redraw
        # of the crossheirs
        if event.button() == Qt.LeftButton:
            self.update_selection(event.pos())
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # these two handle the move and press of the mouse and trigger a redraw
        # of the crossheirs
        if event.buttons() & Qt.LeftButton:
            self.update_selection(event.pos())
        super().mouseMoveEvent(event)

    def update_selection(self, pos):
        # this is called when the color is changed using the widget itself
        # make sure its in bounds
        x = max(0, min(pos.x(), self.size))
        y = max(0, min(pos.y(), self.size))

        # Update the crosshair lines
        self.crosshair_vline_o.setLine(x, 0, x, self.size)  # Vertical stroke
        self.crosshair_hline_o.setLine(0, y, self.size, y)  # Horizontal stroke
        self.crosshair_vline_i.setLine(x, 0, x, self.size)  # Vertical line
        self.crosshair_hline_i.setLine(0, y, self.size, y)  # Horizontal line

        self.sv_changed.emit(x // 2, 255 - (y // 2))

    def set_selection_from_hsv(self, hue, saturation, value):
        # called when the color is changed using the rgb sliders

        x = int((saturation / 255) * self.size)

        y = int(((255 - value) / 255) * self.size)

        self.hue = hue
        self.update_gradient()

        self.crosshair_vline_o.setLine(x, 0, x, self.size)  # Vertical stroke
        self.crosshair_hline_o.setLine(0, y, self.size, y)  # Horizontal stroke
        self.crosshair_vline_i.setLine(x, 0, x, self.size)  # Vertical line
        self.crosshair_hline_i.setLine(0, y, self.size, y)  # Horizontal line

        # self.update()  # Seems to not be needed


class HueWidget(QGraphicsView):
    # Signal to be captured by the HSVWidget
    h_changed = Signal(int)
    # Reset the stylesheet for now. should fix.
    style = """QGraphicsView {
        border: 0px;
        margin: 0px;
        min-width: 0px;
        background: transparent;
        }
    """

    def __init__(self, width=45, height=510, parent=None):
        super().__init__(parent)

        self.setStyleSheet(self.style)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.width = width
        self.height = height

        self.setFixedSize(width, height)
        self._scene = QGraphicsScene(self)

        # set the viewbox
        self._scene.setSceneRect(0, 0, width, height)

        self._rect = QGraphicsRectItem(0, 0, width, height)
        self._rect.setPen(Qt.NoPen)

        self._scene.addItem(self._rect)

        self.setScene(self._scene)

        self.hue_rect = QGraphicsRectItem(0, 0, width, height)

        self.paint_gradient()

        self._scene.setSceneRect(0, 0, width, height)

        # Dark #222323
        # Light #f0f6f0
        # create the inner crosshair (dark line)
        self.crosshair_hline_o = QGraphicsLineItem(
            0, 0, width, 0
        )  # Horizontal line
        self.crosshair_hline_o.setPen(QPen(QColor("#f0f6f0"), 3))

        # create the inner crosshair (light line)
        self.crosshair_hline_i = QGraphicsLineItem(
            0, 0, width, 0
        )  # Horizontal line
        self.crosshair_hline_i.setPen(QPen(QColor("#222323"), 1))

        self._scene.addItem(self.crosshair_hline_o)
        self._scene.addItem(self.crosshair_hline_i)

    def paint_gradient(self):
        # creates the hue gradient using self.generate_hue_gradient
        # and then paints it.
        pixmap = self.generate_hue_gradient(self.width, self.height)
        self._rect.setBrush(QBrush(pixmap))

    @staticmethod
    def generate_hue_gradient(width, height):
        # This creates the gradient, that is the background of the hue widget
        # as a pixmap
        pixmap = QPixmap(width, height)
        painter = QPainter(pixmap)

        for y in range(height):
            color = QColor.fromHsv(y * 360 // height, 255, 255)
            painter.setPen(color)
            painter.drawLine(0, y, width, y)

        painter.end()
        return pixmap

    def mousePressEvent(self, event):
        # these two handle the mouse click and movements and update the selection
        if event.button() == Qt.LeftButton:
            self.update_selection(event.pos())
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # these two handle the mouse click and movements and update the selection
        if event.buttons() & Qt.LeftButton:
            self.update_selection(event.pos())
        super().mouseMoveEvent(event)

    def update_selection(self, pos):
        # called when the color is changed using the widget
        y = max(0, min(pos.y(), self.height))

        self.crosshair_hline_o.setLine(0, y, self.width, y)
        self.crosshair_hline_i.setLine(0, y, self.width, y)

        hue_value = int((y / self.height) * 359)
        hue_value = max(0, min(359, hue_value))

        self.h_changed.emit(hue_value)

    def set_selection_from_hue(self, hue_value):
        # this is called when the color is changed from the RGB sliders
        y = int((hue_value / 359) * self.height)

        # Update the crosshair lines
        self.crosshair_hline_o.setLine(0, y, self.width, y)  # Outer line
        self.crosshair_hline_i.setLine(0, y, self.width, y)  # Inner line

        self.update()  # Force UI to refresh


# Run standalone for testing
if __name__ == "__main__":
    app = QApplication(sys.argv)
    load_qss(app, get_path("res/styles/style.css"))
    dialog = ColorPicker()
    dialog.exec()
