from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QComboBox, QListView
from PySide6.QtCore import Qt, Signal, QPoint
from res_loader import get_path

class GrayscaleCombo(QWidget):
    modeChanged = Signal(str)  # Signal emitted when the algorithm changes

    def __init__(self):
        super().__init__()

        # Initialize UI components
        self._initialize_ui()

    def _initialize_ui(self):
        # Label for the combo box
        self.label = QLabel("Grayscale Mode")

        # ComboBox for algorithm selection
        self.combobox = self._create_combobox()

        # Connect signal for algorithm change
        self.combobox.currentTextChanged.connect(self.emit_mode_changed)

        # Layout to contain the label and combo box
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combobox)

        self.setLayout(self.layout)

    def _create_combobox(self):
        """
        Creates and returns a QComboBox with the grayscale modes.

        Returns:
            QComboBox: The combo box with the available grayscale modes.
        """
        combobox = QComboBox()
        modes = [
            "Luminance", "Luma", "Lightness", "Average", "Value"
        ]
        combobox.addItems(modes)
        combobox.setView(QListView())  # Ensure dropdown uses a list view for better presentation
        return combobox

    def emit_mode_changed(self, text):
        """Emit the modeChanged signal with the selected mode."""
        self.modeChanged.emit(text)
        print(f"Selected mode: {text}")

    def showPopup(self):
        """Found this suggested somewhere on stackexchange. Doesn't really seem to work."""
        super().showPopup()
        # Move the popup to the top left of the combobox to control position
        self.view().window().move(self.mapToGlobal(QPoint(0, self.height())))
