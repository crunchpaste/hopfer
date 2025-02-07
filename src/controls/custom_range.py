from PySide6.QtWidgets import QApplication, QStyleOptionSlider
from PySide6.QtCore import Qt
from PySide6.QtGui import QFocusEvent, QBrush, QColor
from superqt.sliders._range_style import RangeSliderStyle
from superqt import QRangeSlider

class CustomRangeSliderStyle(RangeSliderStyle):
    def thickness(self, opt: QStyleOptionSlider) -> float:
        """Override thickness calculation to add 2px."""
        base_thickness = super().thickness(opt)
        return base_thickness + 3  # Very hacky

class RangeSlider(QRangeSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style = CustomRangeSliderStyle()
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def focusInEvent(self, event: QFocusEvent):
        """Called when the slider gains focus."""
        self.setProperty("barColor", QBrush(QColor("#fa8072")))
        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent):
        """Called when the slider loses focus."""
        self.setProperty("barColor", QBrush(QColor("#f0f6f0")))
        super().focusOutEvent(event)
