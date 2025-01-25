from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QApplication
import sys

class ProcessingIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("processing-indicator")
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        # Create a label
        self.label = QLabel("Processing...", self)

        # Create a layout and add the label to it
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

        # Timer to update the label text
        self.dot_count = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_label)
        self.timer.start(500)  # Update every 500ms

    def update_label(self):
        # Animate the dots
        self.dot_count = (self.dot_count + 1) % 4
        dots = '.' * self.dot_count
        self.label.setText(f"Processing{dots}")
