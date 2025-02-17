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

        button_size = QSize(30, 30)

        for button in titlebar_buttons:
            button.setFixedSize(button_size)
            button._normalColor = QColor("#6a6d6b")
            button._hoverColor = QColor("salmon")
            button._pressedColor = QColor("#f0f6f0")
            self.hBoxLayout.addWidget(button, 0, Qt.AlignRight)

            self.hBoxLayout.addSpacerItem(
                QSpacerItem(10, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
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

    def resizeEvent(self, event):
        # Otherwise the icon does not change when the titlebar is double clicked
        super().resizeEvent(event)

        if self.window().isMaximized():
            self.maxBtn.setIcon(get_path("res/icons/collapse.svg"))
        else:
            self.maxBtn.setIcon(get_path("res/icons/expand.svg"))


class DialogTitleBar(TitleBar):
    """Custom title bar for the preferences dialog"""

    def __init__(self, parent):
        super().__init__(parent)
        # Remove old buttons from layout to replace with SVG versions
        self.hBoxLayout.removeWidget(self.minBtn)
        self.minBtn.setParent(None)
        self.minBtn.deleteLater()

        self.hBoxLayout.removeWidget(self.maxBtn)
        self.maxBtn.setParent(None)
        self.maxBtn.deleteLater()

        self.hBoxLayout.removeWidget(self.closeBtn)
        self.closeBtn.setParent(None)
        self.closeBtn.deleteLater()

        # self.hBoxLayout.update()
        # self.update()

        self.hBoxLayout.addStretch()

        spacer = QSpacerItem(
            13, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum
        )
        self.closeBtn = HCloseButton(
            iconPath=get_path("res/icons/close.svg"), parent=self
        )

        button_size = QSize(30, 30)

        self.closeBtn.setFixedSize(button_size)
        self.closeBtn._normalColor = QColor("#6a6d6b")
        self.closeBtn._hoverColor = QColor("salmon")
        self.closeBtn._pressedColor = QColor("#f0f6f0")
        self.hBoxLayout.addWidget(self.closeBtn, 0, Qt.AlignRight)

        self.hBoxLayout.addSpacerItem(spacer)

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


class HSvgTitleBarButton(SvgTitleBarButton):
    """Title bar button using svg icon"""

    def __init__(self, iconPath, parent=None):
        super().__init__(iconPath, parent)
        self.setObjectName("HSvgButton")

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        color, bgColor = self._getColors()

        # Draw circular background (centered)
        painter.setBrush(bgColor)
        painter.setPen(Qt.NoPen)

        # draw background
        size = min(self.width(), self.height())  # Ensure it fits within the widget
        center = self.rect().center()  # Get center of widget
        radius = size // 2  # Radius of the circle

        painter.drawEllipse(center.x() - radius, center.y() - radius, size, size)

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
        self.setHoverBackgroundColor(QColor("#1c1d1d"))
        self.setPressedBackgroundColor(QColor("#1c1d1d"))


# Custom Maximize Button (using SVG)
class HMaximizeButton(HSvgTitleBarButton):
    """Maximize button with SVG icon"""

    def __init__(self, iconPath=":/qframelesswindow/maximize.svg", parent=None):
        super().__init__(iconPath, parent)
        self._isMax = False
        self.setHoverColor(Qt.white)
        self.setPressedColor(Qt.white)
        self.setHoverBackgroundColor(QColor("#1c1d1d"))
        self.setPressedBackgroundColor(QColor("#1c1d1d"))

    def setMaxState(self, isMax):
        pass


# Custom Close Button (using SVG)
class HCloseButton(HSvgTitleBarButton):
    """Close button with SVG icon"""

    def __init__(self, iconPath=":/qframelesswindow/close.svg", parent=None):
        super().__init__(iconPath, parent)
        self.setHoverColor(Qt.white)
        self.setPressedColor(Qt.white)
        self.setHoverBackgroundColor(QColor("#1c1d1d"))
        self.setPressedBackgroundColor(QColor("#1c1d1d"))
