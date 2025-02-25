from PySide6.QtGui import QPainter
from PySide6.QtWidgets import (
    QApplication,
    QProxyStyle,
    QStyle,
    QStyleOption,
    QWidget,
)


class NoFocusProxyStyle(QProxyStyle):
    # this is a very very hacky solution to remove the focus frame, which for some reason is not stylable using QSS.
    def __init__(self, base_style=None):
        super().__init__(base_style or QApplication.style())

    def drawPrimitive(
        self,
        element: QStyle.PrimitiveElement,
        option: QStyleOption,
        painter: QPainter,
        widget: QWidget,
    ) -> None:
        # If the element is the focus rectangle, do not draw it
        if element == QStyle.PE_FrameFocusRect:
            return

        super().drawPrimitive(element, option, painter, widget)
