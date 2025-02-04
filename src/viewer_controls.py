import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QApplication
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from res_loader import get_path

class ViewerControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("viewer-controls")
        # Create the layout
        layout = QHBoxLayout()

        icon_path = get_path("res/icons")

        _ext = "svg"

        self.fit = self._create_button(
            "e3dc",
            "Fit to viewer")
        self.fit.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.x1 = self._create_button(
            "efcd",
            "Original size")
        self.x1.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.x2 = self._create_button(
            "f4eb",
            "Double size")
        self.x2.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.blur = self._create_button(
            "eb77",
            "Blur preview")
        self.blur.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        layout.addStretch()
        layout.addWidget(self.x1)
        layout.addWidget(self.x2)
        layout.addWidget(self.fit)
        layout.addWidget(self.blur)

        # Set the layout for the widget
        self.setLayout(layout)

    def _create_button(self, unicode, tooltip, click_handler=None):
        """
        Creates a button with the specified icons, tooltip, and click handler.

        Args:
            unicode (str): The unicode provided by google fonts
            tooltip (str): Tooltip text for the button.
            click_handler (function or None): Function to connect to the button click event.

        Returns:
            QPushButton: The configured QPushButton.
        """
        icon_unicode = chr(int(unicode, 16))
        button = QPushButton(icon_unicode)
        button.setToolTip(tooltip)

        if click_handler:
            button.clicked.connect(click_handler)

        return button
