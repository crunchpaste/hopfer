from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QTabWidget, QVBoxLayout, QWidget

from status import NotificationPane
from tabs import HalftoneTab, ImageTab, OutputTab
from toolbox import Toolbox


class SideBar(QWidget):
    def __init__(self, main_window, writer=None):
        super().__init__()

        self.main_window = main_window

        self.writer = writer

        self.layout = QHBoxLayout()
        self.secondary_layout = QVBoxLayout()

        self.toolbox = Toolbox(
            main_window=self.main_window,
            writer=self.writer,
        )
        self.tabs = QTabWidget()

        self.notifications = NotificationPane(self)

        # Add individual tabs
        # self.image_tab = ImageTab(self.processor)
        # self.halftone_tab = HalftoneTab(self.processor)
        # self.output_tab = OutputTab(self.storage)

        self.image_tab = ImageTab(writer=self.writer, window=self.main_window)
        self.halftone_tab = HalftoneTab(
            writer=self.writer, window=self.main_window
        )
        self.output_tab = OutputTab(writer=self.writer, window=self.main_window)

        self.tabs.addTab(self.image_tab, "Image")
        self.tabs.addTab(self.halftone_tab, "Halftone")
        self.tabs.addTab(self.output_tab, "Output")

        self.tabs.tabBar().setFocusPolicy(Qt.FocusPolicy.TabFocus)

        self.layout.addWidget(self.toolbox)
        self.secondary_layout.addWidget(self.tabs)
        self.secondary_layout.addWidget(self.notifications)

        self.layout.addLayout(self.secondary_layout)
        self.setLayout(self.layout)

    def activateTab(self, tab_index):
        if tab_index == 1:
            self.tabs.setCurrentIndex(tab_index)
            self.halftone_tab.combobox.combobox.setFocus()
        else:
            self.tabs.setCurrentIndex(0)
            self.image_tab.combobox.combobox.setFocus()
