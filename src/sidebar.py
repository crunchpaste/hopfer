from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QPushButton
from PySide6.QtGui import QShortcut, QKeySequence, QIcon
from PySide6.QtCore import QSize
from tabs import ImageTab, HalftoneTab
from status import NotificationPane
from toolbox import Toolbox

class SideBar(QWidget):
    def __init__(self, processor, storage):
        super().__init__()
        self.storage = storage
        self.processor = processor
        self.layout = QHBoxLayout()
        self.secondary_layout = QVBoxLayout()

        self.toolbox = Toolbox(storage)
        # Create the tabs container
        self.tabs = QTabWidget()

        self.notifications = NotificationPane(self)

        # Add individual tabs
        self.file_tab = ImageTab(self.processor)
        self.halftone_tab = HalftoneTab(self.processor)

        self.tabs.addTab(self.file_tab, "Image")
        self.tabs.addTab(self.halftone_tab, "Halftone")

        self.layout.addWidget(self.toolbox)
        self.secondary_layout.addWidget(self.tabs)
        self.secondary_layout.addWidget(self.notifications)

        self.layout.addLayout(self.secondary_layout)
        self.setLayout(self.layout)
