from PySide6.QtCore import Qt
from PySide6.QtGui import QFocusEvent
from superqt import QRangeSlider


class RangeSlider(QRangeSlider):
    """
    For some reason superqt does not expose direct control over the look of
    the range bar so subclassing the QRangeSlider was needed in order to make
    it fit the look of the rest of the sliders.
    """

    def __init__(self, *args, colors=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.colors = colors
        self._style.pen_active = self.colors.primary
        self._style.pen_inactive = self.colors.primary
        self._style.pen_disabled = self.colors.primary
        self._style.brush_active = self.colors.primary
        self._style.brush_inactive = self.colors.primary
        self._style.brush_disabled = self.colors.primary

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def focusInEvent(self, event: QFocusEvent):
        """Called when the slider gains focus."""
        self._style.pen_active = self.colors.accent
        self._style.pen_inactive = self.colors.accent
        self._style.pen_disabled = self.colors.accent
        self._style.brush_active = self.colors.accent
        self._style.brush_inactive = self.colors.accent
        self._style.brush_disabled = self.colors.accent

        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent):
        """Called when the slider loses focus."""
        self._style.pen_active = self.colors.primary
        self._style.pen_inactive = self.colors.primary
        self._style.pen_disabled = self.colors.primary
        self._style.brush_active = self.colors.primary
        self._style.brush_inactive = self.colors.primary
        self._style.brush_disabled = self.colors.primary

        super().focusOutEvent(event)

    def update_slider(self):
        self._style.pen_active = self.colors.primary
        self._style.pen_inactive = self.colors.primary
        self._style.pen_disabled = self.colors.primary
        self._style.brush_active = self.colors.primary
        self._style.brush_inactive = self.colors.primary
        self._style.brush_disabled = self.colors.primary
        self.repaint()
