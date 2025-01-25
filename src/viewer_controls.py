import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QApplication
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from superqt import QIconifyIcon
from res_loader import get_path

class ViewerControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("viewer-controls")
        # Create the layout
        layout = QHBoxLayout()

        icon_path = get_path("res/icons")

        if os.name == 'nt':
            _ext = "png"
        else:
            _ext = "svg"

        # Add buttons to the layout
        # self.fit = QPushButton()
        # self.fit.setIcon(QIconifyIcon("material-symbols:filter-center-focus",
        #                               color='#f0f6f0'))
        # self.fit.setIconSize(QSize(22,22))
        # self.fit.setFixedSize(34, 34)

        self.fit = self._create_button(
            icon_path + f"/fit.{_ext}",
            icon_path + f"/dark/fit.{_ext}",
            icon_path + f"/salmon/fit.{_ext}",
            icon_path + f"/disabled/fit.{_ext}",
            "Fit to viewer")
        self.fit.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.x1 = self._create_button(
            icon_path + f"/1x.{_ext}",
            icon_path + f"/dark/1x.{_ext}",
            icon_path + f"/salmon/1x.{_ext}",
            icon_path + f"/disabled/1x.{_ext}",
            "Original size")
        self.x1.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.x2 = self._create_button(
            icon_path + f"/2x.{_ext}",
            icon_path + f"/dark/2x.{_ext}",
            icon_path + f"/salmon/2x.{_ext}",
            icon_path + f"/disabled/2x.{_ext}",
            "Double size")
        self.x2.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.blur = self._create_button(
            icon_path + f"/blur.{_ext}",
            icon_path + f"/dark/blur.{_ext}",
            icon_path + f"/salmon/blur.{_ext}",
            icon_path + f"/disabled/blur.{_ext}",
            "Blur preview")
        self.blur.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        layout.addStretch()
        layout.addWidget(self.x1)
        layout.addWidget(self.x2)
        layout.addWidget(self.fit)
        layout.addWidget(self.blur)

        # Set the layout for the widget
        self.setLayout(layout)

    def _create_button(self, icon_default, icon_hover, icon_focus, icon_disabled, tooltip, click_handler=None):
        """
        Creates a button with the specified icons, tooltip, and click handler.

        Args:
            icon_default (str): Path to the default icon.
            icon_hover (str): Path to the icon on hover.
            icon_focus (str): Path to the icon on focus.
            tooltip (str): Tooltip text for the button.
            click_handler (function or None): Function to connect to the button click event.

        Returns:
            QPushButton: The configured QPushButton.
        """
        button = QPushButton("")
        button.setIcon(QIcon(icon_default))
        button.setIconSize(QSize(20, 20))  # Icon size
        button.setStyleSheet(
            f'QPushButton:hover {{ icon: url({icon_hover}); }}'
            f'QPushButton:focus {{ icon: url({icon_focus}); }}'
            f'QPushButton:disabled {{ icon: url({icon_disabled}); }}'
        )
        button.setToolTip(tooltip)

        if click_handler:
            button.clicked.connect(click_handler)

        return button
