from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QSizePolicy, QSpacerItem
from qframelesswindow import SvgTitleBarButton, TitleBar

from res_loader import get_path


class HopferTitleBar(TitleBar):
    """Custom title bar"""

    def __init__(self, parent):
        super().__init__(parent)
        # Remove old buttons from layout to replace with SVG versions
        self.hBoxLayout.removeWidget(self.minBtn)
        self.hBoxLayout.removeWidget(self.maxBtn)
        self.hBoxLayout.removeWidget(self.closeBtn)
        self.minBtn.deleteLater()
        self.maxBtn.deleteLater()
        self.closeBtn.deleteLater()

        # Add an svg logotype instead of label to avoid font import
        self.logo = QSvgWidget(get_path("res/w_icon.svg"))
        # this is the actual size of the svg
        self.logo.setFixedSize(81, 40)
        self.logo.renderer().setAspectRatioMode(Qt.KeepAspectRatio)
        self.hBoxLayout.insertWidget(0, self.logo)
        self.hBoxLayout.insertStretch(1)

        spacer = QSpacerItem(
            13, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum
        )

        self.hBoxLayout.insertSpacerItem(0, spacer)

        # Material design icons instead of the windows one provided by qframelesswindow
        self.minBtn = HMinimizeButton(
            iconPath=get_path("res/icons/minimize.svg"), parent=self
        )
        self.maxBtn = HMaximizeButton(
            iconPath=get_path("res/icons/expand.svg"), parent=self
        )
        self.closeBtn = HCloseButton(
            iconPath=get_path("res/icons/close.svg"), parent=self
        )

        titlebar_buttons = [self.minBtn, self.maxBtn, self.closeBtn]

        button_size = QSize(20, 20)

        for button in titlebar_buttons:
            button.setFixedSize(button_size)
            button._normalColor = QColor("#6a6d6b")
            button._hoverColor = QColor("salmon")
            button._pressedColor = QColor("#f0f6f0")
            self.hBoxLayout.addWidget(button, 0, Qt.AlignRight)

            self.hBoxLayout.addSpacerItem(
                QSpacerItem(15, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
            )

        # Connect buttons to window actions
        self.minBtn.clicked.connect(parent.showMinimized)
        self.maxBtn.clicked.connect(self.toggleMaxRestore)
        self.closeBtn.clicked.connect(parent.close)

        self.setFixedHeight(45)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("customTitleBar")
        self.setStyleSheet("""
            #customTitleBar {
                background: #202121;
                border-bottom: 2px solid #192020;
            }
        """)

    def toggleMaxRestore(self):
        """Toggle between maximized and normal state."""
        if self.window().isMaximized():
            self.window().showNormal()
            self.maxBtn.setIcon(get_path("res/icons/expand.svg"))
        else:
            self.window().showMaximized()
            self.maxBtn.setIcon(get_path("res/icons/collapse.svg"))


class HSvgTitleBarButton(SvgTitleBarButton):
    """Title bar button using svg icon"""

    def __init__(self, iconPath, parent=None):
        super().__init__(iconPath, parent)
        self.setObjectName("HSvgButton")
        print(f"Object Name: {self.objectName()}")  # Debug print

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        color, bgColor = self._getColors()

        # draw background
        painter.setBrush(bgColor)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())

        # draw icon
        color = color.name()
        pathNodes = self._svgDom.elementsByTagName("path")
        for i in range(pathNodes.length()):
            element = pathNodes.at(i).toElement()
            element.setAttribute("fill", color)

        renderer = QSvgRenderer(self._svgDom.toByteArray())
        renderer.render(painter, QRectF(self.rect()))


# Custom Minimize Button (using SVG)
class HMinimizeButton(HSvgTitleBarButton):
    """Minimize button with SVG icon"""

    def __init__(self, iconPath=":/qframelesswindow/minimize.svg", parent=None):
        super().__init__(iconPath, parent)
        self.setHoverColor(Qt.white)
        self.setPressedColor(Qt.white)
        self.setHoverBackgroundColor(QColor("transparent"))
        self.setPressedBackgroundColor(QColor("transparent"))


# Custom Maximize Button (using SVG)
class HMaximizeButton(HSvgTitleBarButton):
    """Maximize button with SVG icon"""

    def __init__(self, iconPath=":/qframelesswindow/maximize.svg", parent=None):
        super().__init__(iconPath, parent)
        self._isMax = False
        self.setHoverColor(Qt.white)
        self.setPressedColor(Qt.white)
        self.setHoverBackgroundColor(QColor("transparent"))
        self.setPressedBackgroundColor(QColor("transparent"))

    def setMaxState(self, isMax):
        pass


# Custom Close Button (using SVG)
class HCloseButton(HSvgTitleBarButton):
    """Close button with SVG icon"""

    def __init__(self, iconPath=":/qframelesswindow/close.svg", parent=None):
        super().__init__(iconPath, parent)
        self.setHoverColor(Qt.white)
        self.setPressedColor(Qt.white)
        self.setHoverBackgroundColor(QColor("transparent"))
        self.setPressedBackgroundColor(QColor("transparent"))
