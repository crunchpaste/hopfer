from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton


class NotificationPane(QFrame):
    """This one is meant to display all sorts of errors, warnings and other notifications. Currently it is mainly used to display an "Image saved" message."""

    def __init__(self, parent):
        super().__init__(parent)

        self.setObjectName("notificationPane")

        self.parent = parent

        # Layout setup
        self.layout = QHBoxLayout(self)
        self.message_label = QLabel("", self)
        self.message_label.setWordWrap(True)
        self.layout.addWidget(self.message_label)

        # Close button setup with an "X" icon
        self.close_button = QPushButton("✕", self)
        self.close_button.setFixedSize(20, 20)
        self.close_button.setStyleSheet(
            """
            QPushButton {
                border: none;
                color: white;
                font-size: 16px;
                max-width: 20px;
            }
            QPushButton:hover {
                color: salmon;
            }
        """
        )
        self.close_button.clicked.connect(self.fade_out)
        self.layout.addWidget(self.close_button, alignment=Qt.AlignmentFlag.AlignTop)

        # Initially hidden
        self.setVisible(False)

    def show_notification(self, message, duration=3000):
        """Display the notification with a message for a specified duration."""
        self.message_label.setText(message)
        self.setMaximumWidth(self.parent.width())
        self.setVisible(True)

        QTimer.singleShot(duration, self.fade_out)

    def fade_out(self):
        self.setVisible(False)
