from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QComboBox, QListView
from PySide6.QtCore import Qt, Signal, QPoint
from res_loader import get_path

class HalftoneCombo(QWidget):
    algorithmChanged = Signal(str)  # Signal emitted when the algorithm changes

    def __init__(self):
        super().__init__()

        # Initialize UI components
        self._initialize_ui()

    def _initialize_ui(self):
        # Label for the combo box
        self.label = QLabel("Halftoning Algorithm")

        # ComboBox for algorithm selection
        self.combobox = self._create_combobox()

        # Connect signal for algorithm change
        self.combobox.currentTextChanged.connect(self.emit_algorithm_changed)

        # Layout to contain the label and combo box
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combobox)

        self.setLayout(self.layout)

    def _create_combobox(self):
        """
        Creates and returns a QComboBox with the halftoning algorithms.

        Returns:
            QComboBox: The combo box with the available halftoning algorithms.
        """
        combobox = QComboBox()
        algorithms = [
            "None", "Threshold", "Sauvola threshold", "Phansalkar threshold", "Mezzotint", "Mezzotint Gauss", "Mezzotint beta", "Floyd-Steinberg", "False Floyd-Steinberg", "Jarvis", "Stucki", "Stucki small", "Stucki large", "Atkinson", "Burkes", "Sierra", "Sierra2", "Sierra2 4A", "Nakano"
        ]
        combobox.addItems(algorithms)
        combobox.setView(QListView())  # Ensure dropdown uses a list view for better presentation
        return combobox

    def emit_algorithm_changed(self, text):
        """Emit the algorithmChanged signal with the selected algorithm."""
        self.algorithmChanged.emit(text)
        print(f"Selected algorithm: {text}")

    def showPopup(self):
        """Found this suggested somewhere on stackexchange. Doesn't really seem to work."""
        super().showPopup()
        # Move the popup to the top left of the combobox to control position
        self.view().window().move(self.mapToGlobal(QPoint(0, self.height())))
