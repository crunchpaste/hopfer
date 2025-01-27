from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget, QLabel, QPushButton, QSpacerItem, QSizePolicy, QTextEdit
from PySide6.QtCore import Qt, QUrl
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtGui import QDesktopServices
from res_loader import get_path

# Quite messy should fix at some point

def open_url(url):
    QDesktopServices.openUrl(QUrl(url))

class ShortcutLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text)
        self.setObjectName("shortcut")

class ShortcutLayout(QWidget):
    def __init__(self, label, sc_list):
        super().__init__()
        layout = QHBoxLayout()
        action = QLabel(label)

        layout.addWidget(action)
        layout.addStretch()

        for sc in sc_list:
            layout.addWidget(ShortcutLabel(sc))

        self.setLayout(layout)


class ShortcutsTab(QWidget):
    def __init__(self, dialog):
        super().__init__()
        self.dialog = dialog
        layout = QVBoxLayout()

        shortcuts = [
            ShortcutLayout("Quit",["Ctrl","Q"]),
            ShortcutLayout("Open image",["Ctrl","O"]),
            ShortcutLayout("Save image",["Ctrl","S"]),
            ShortcutLayout("Save image as",["Ctrl","Shift","S"]),
            ShortcutLayout("Image tab",["Ctrl","I"]),
            ShortcutLayout("Haltone tab",["Ctrl","H"]),
            ShortcutLayout("Blur preview",["Ctrl","B"]),
            ShortcutLayout("Zoom level",["Ctrl","0-9"])
        ]

        for sc in shortcuts:
            layout.addWidget(sc)

        self.setLayout(layout)

class AboutTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        with open(get_path("res/desc.html"), "r") as file:
            text = file.read()
        description_label = QLabel()
        description_label.setObjectName("about")
        description_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        description_label.setWordWrap(True)
        description_label.setTextFormat(Qt.MarkdownText)
        description_label.setText(text)
        description_label.setOpenExternalLinks(True)
        layout.addWidget(description_label)

        layout.addStretch()

        developer_label = QLabel("Pavel Lefterov")
        developer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(developer_label)

        license_label = QLabel("Licensed under GPLv3 License")
        license_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(license_label)

        links_layout = QHBoxLayout()
        github_link = QPushButton("GitHub")
        links_layout.addWidget(github_link)
        github_link.clicked.connect(lambda: open_url(
                "https://github.com/crunchpaste/hopfer"))

        layout.addLayout(links_layout)


        self.setLayout(layout)

class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.setModal(True)
        # self.setWindowFlag(Qt.FramelessWindowHint)
        self.setFixedSize(445,720)
        layout = QVBoxLayout()

        self.logotype = QSvgWidget(get_path("res/type.svg"))
        self.logotype.renderer().setAspectRatioMode(Qt.KeepAspectRatio)
        self.logotype.setObjectName("logotype")
        layout.addWidget(self.logotype)

        with open(get_path("res/hash.txt"), "r") as file:
            hash = file.read()

        self.version_label = QLabel(f"prealpha+{hash}")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.version_label)

        spacer = QSpacerItem(0, 50, QSizePolicy.Fixed, QSizePolicy.Minimum)
        layout.addItem(spacer)

        self.tabs = QTabWidget()
        self.tabs.setFixedSize(420, 462)

        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)  # Closes the dialog

        self.tabs.addTab(AboutTab(), "About")
        self.tabs.addTab(ShortcutsTab(self), "Shortcuts")
        layout.addWidget(self.tabs)

        self.setLayout(layout)
