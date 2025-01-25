from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QApplication
from PySide6.QtCore import Qt, QSize
from superqt import QIconifyIcon

class ViewerControls(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("viewer-controls")
        # Create the layout
        layout = QHBoxLayout()

        # Add buttons to the layout
        self.fit = QPushButton()
        self.fit.setIcon(QIconifyIcon("material-symbols:filter-center-focus",
                                      color='#f0f6f0'))
        self.fit.setIconSize(QSize(22,22))
        self.fit.setFixedSize(34, 34)
        self.fit.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.x1 = QPushButton()
        self.x1.setIcon(QIconifyIcon("material-symbols:1x-mobiledata",
                                     color='#f0f6f0'))
        self.x1.setIconSize(QSize(22,22))
        self.x1.setFixedSize(34, 34)
        self.x1.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.x2 = QPushButton()
        self.x2.setIcon(QIconifyIcon("material-symbols:speed-2x",
                                     color='#f0f6f0'))
        self.x2.setIconSize(QSize(22,22))
        self.x2.setFixedSize(34, 34)
        self.x2.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.blur = QPushButton()
        self.blur.setIcon(QIconifyIcon("material-symbols:deblur",
                                     color='#f0f6f0'))
        self.blur.setIconSize(QSize(22,22))
        self.blur.setFixedSize(34, 34)
        self.blur.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        layout.addStretch()
        layout.addWidget(self.x1)
        layout.addWidget(self.x2)
        layout.addWidget(self.fit)
        layout.addWidget(self.blur)

        # Set the layout for the widget
        self.setLayout(layout)
