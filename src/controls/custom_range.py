from PySide6.QtCore import Qt
from PySide6.QtGui import QFocusEvent
from superqt import QRangeSlider


class RangeSlider(QRangeSlider):
    """
    For some reason superqt does not expose direct control over the look of
    the range bar so subclassing the QRangeSlider was needed in order to make
    it fit the look of the rest of the sliders.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style.pen_active = "#f0f6f0"
        self._style.pen_inactive = "#f0f6f0"
        self._style.pen_disabled = "#f0f6f0"
        self._style.brush_active = "#f0f6f0"
        self._style.brush_inactive = "#f0f6f0"
        self._style.brush_disabled = "#f0f6f0"

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def focusInEvent(self, event: QFocusEvent):
        """Called when the slider gains focus."""
        self._style.pen_active = "#fa8072"
        self._style.pen_inactive = "#fa8072"
        self._style.pen_disabled = "#fa8072"
        self._style.brush_active = "#fa8072"
        self._style.brush_inactive = "#fa8072"
        self._style.brush_disabled = "#fa8072"

        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent):
        """Called when the slider loses focus."""
        self._style.pen_active = "#f0f6f0"
        self._style.pen_inactive = "#f0f6f0"
        self._style.pen_disabled = "#f0f6f0"
        self._style.brush_active = "#f0f6f0"
        self._style.brush_inactive = "#f0f6f0"
        self._style.brush_disabled = "#f0f6f0"

        super().focusOutEvent(event)
