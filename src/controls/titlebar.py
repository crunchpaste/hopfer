from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QLabel, QSizePolicy, QSpacerItem
from qframelesswindow import SvgTitleBarButton, TitleBar

from controls.focus_widget import FocusWidget
from res_loader import get_path, load_svg


class HopferTitleBar(TitleBar):
    """Custom title bar"""

    def __init__(self, parent):
        super().__init__(parent)

        self.dark = False
        self.colors = parent.colors
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

        # Add an svg logotype instead of label to avoid font import
        self.logo = QSvgWidget()
        self.logo.load(load_svg(get_path("res/w_icon.svg"), self.colors))
        # this is the actual size of the svg
        self.logo.setFixedSize(71, 35)
        self.logo.renderer().setAspectRatioMode(Qt.KeepAspectRatio)
        self.focus = FocusWidget()

        self.hBoxLayout.insertWidget(0, self.logo)
        self.hBoxLayout.addWidget(self.focus)
        self.hBoxLayout.addStretch()

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

        self.titlebar_buttons = [self.minBtn, self.maxBtn, self.closeBtn]

        button_size = QSize(30, 30)

        for button in self.titlebar_buttons:
            button.setFocusPolicy(Qt.NoFocus)
            button.setFixedSize(button_size)
            # button._normalColor = QColor("#6a6d6b")
            # button._hoverColor = QColor("salmon")
            # button._pressedColor = QColor("#f0f6f0")
            self.set_button_colors()
            self.hBoxLayout.addWidget(button, 0, Qt.AlignRight)

            self.hBoxLayout.addSpacerItem(
                QSpacerItem(
                    10, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum
                )
            )

        # Connect buttons to window actions
        self.minBtn.clicked.connect(parent.showMinimized)
        self.maxBtn.clicked.connect(self.toggleMaxRestore)
        self.closeBtn.clicked.connect(parent.close)

        self.setFixedHeight(45)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("customTitleBar")
        self.logo.setObjectName("titleBarLogo")
        # self.setStyleSheet("""
        #     #customTitleBar {
        #         background: #202121;
        #         border-bottom: 2px solid #192020;
        #     }
        # """)

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

    def change_theme(self):
        self.logo.load(load_svg(get_path("res/w_icon.svg"), self.colors))
        self.set_button_colors()

    def set_button_colors(self):
        for button in self.titlebar_buttons:
            button._normalColor = QColor(self.colors.disabled)
            button._hoverColor = QColor(self.colors.accent)
            button._pressedColor = QColor(self.colors.primary)
            button._hoverBgColor = QColor(self.colors.titlebar_btn)
            button._pressedBgColor = QColor(self.colors.titlebar_btn)
            # else:
            #     button._normalColor = QColor(self.colors.disabled)
            #     button._hoverColor = QColor(self.colors.accent)
            #     button._pressedColor = QColor(self.colors.primary)
            #     button._hoverBgColor = QColor(self.colors.titlebar_btn)
            #     button._pressedBgColor = QColor(self.colors.titlebar_btn)


class DialogTitleBar(TitleBar):
    """Custom title bar for the preferences dialog"""

    def __init__(self, parent, colors, label=None):
        super().__init__(parent)
        self.colors = colors
        self._isDoubleClickEnabled = False
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

        if label is not None:
            self.label = QLabel(label)
            self.label.setStyleSheet("background: transparent")
            label_spacer = QSpacerItem(
                20, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum
            )
            self.hBoxLayout.insertSpacerItem(0, label_spacer)
            self.hBoxLayout.insertWidget(1, self.label)

        self.hBoxLayout.addStretch()

        # adding the focus widget to be able to reset the focus
        self.focus = FocusWidget()
        self.hBoxLayout.addWidget(self.focus)

        spacer = QSpacerItem(
            13, 0, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum
        )
        self.closeBtn = HCloseButton(
            iconPath=get_path("res/icons/close.svg"), parent=self
        )

        button_size = QSize(30, 30)

        self.closeBtn.setFixedSize(button_size)
        # self.closeBtn._normalColor = QColor("#6a6d6b")
        # self.closeBtn._hoverColor = QColor("salmon")
        # self.closeBtn._pressedColor = QColor("#f0f6f0")
        self.set_button_colors()
        self.hBoxLayout.addWidget(self.closeBtn, 0, Qt.AlignRight)

        self.hBoxLayout.addSpacerItem(spacer)

        self.closeBtn.clicked.connect(parent.close)

        self.setFixedHeight(45)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("customTitleBar")
        # self.setStyleSheet("""
        #     #customTitleBar {
        #         background: #202121;
        #         border-bottom: 2px solid #192020;
        #     }color
        # """)

    def set_button_colors(self):
        self.closeBtn._normalColor = QColor(self.colors.disabled)
        self.closeBtn._hoverColor = QColor(self.colors.accent)
        self.closeBtn._pressedColor = QColor(self.colors.primary)
        self.closeBtn._hoverBgColor = QColor(self.colors.titlebar_btn)
        self.closeBtn._pressedBgColor = QColor(self.colors.titlebar_btn)


class HSvgTitleBarButton(SvgTitleBarButton):
    """Title bar button using svg icon"""

    def __init__(self, iconPath, parent=None):
        super().__init__(iconPath, parent)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setObjectName("HSvgButton")

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.Antialiasing | QPainter.SmoothPixmapTransform
        )
        color, bgColor = self._getColors()

        painter.setBrush(bgColor)
        painter.setPen(Qt.NoPen)

        # draw background
        size = min(self.width(), self.height())
        center = self.rect().center()
        radius = (size - 2) // 2

        painter.drawEllipse(
            center.x() - radius, center.y() - radius, size, size
        )

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
