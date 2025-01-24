from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QApplication
from PySide6.QtCore import QSize
from superqt import QIconifyIcon

class ViewerControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Create the layout
        layout = QHBoxLayout()

        # Add buttons to the layout
        self.fit = QPushButton()
        self.fit.setIcon(QIconifyIcon("material-symbols:filter-center-focus"))
        self.fit.setIconSize(QSize(18,18))
        self.fit.setFixedSize(34, 34)

        self.x1 = QPushButton()
        self.x1.setIcon(QIconifyIcon("material-symbols:1x-mobiledata"))
        self.x1.setIconSize(QSize(18,18))
        self.x1.setFixedSize(34, 34)

        self.x2 = QPushButton()
        self.x2.setIcon(QIconifyIcon("material-symbols:speed-2x"))
        self.x2.setIconSize(QSize(18,18))
        self.x2.setFixedSize(34, 34)

        layout.addStretch()
        layout.addWidget(self.fit)
        layout.addWidget(self.x1)
        layout.addWidget(self.x2)

        # Set the layout for the widget
        self.setLayout(layout)
