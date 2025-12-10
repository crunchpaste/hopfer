from PySide6.QtCore import QPoint, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QListView,
    QVBoxLayout,
    QWidget,
)


class GrayscaleCombo(QWidget):
    modeChanged = Signal(str)  # Signal emitted when the algorithm changes

    def __init__(self, colors):
        super().__init__()
        # Initialize UI components
        self.colors = colors
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

        # it seems that some custom margins are needed for some reason
        self.layout.setContentsMargins(7, 10, 7, 10)

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
            "Luminance",
            "Luma",
            "Lightness",
            "Average",
            "Value",
            "Manual RGB",
        ]

        list_view = QListView()
        combobox.setView(list_view)

        combobox.addItems(modes)

        # HACK: fixes the ugly shadow behind the dropdown
        # found on stackoverflow:
        # https://stackoverflow.com/questions/54315474/how-to-remove-white-background-on-top-and-bottom-from-popup-of-qcombobox

        # combobox.view().parentWidget().setStyleSheet(f'background-color: {self.colors.secondary}')
        combobox.setProperty("no-native-popup", True)
        print(combobox.view().parentWidget())

        return combobox

    def emit_mode_changed(self, text):
        """Emit the modeChanged signal with the selected mode."""

        self.modeChanged.emit(text)

    def showPopup(self):
        """Found this suggested somewhere on stackexchange. Doesn't really seem to work."""
        super().showPopup()
        # Move the popup to the top left of the combobox to control position
        self.view().window().move(self.mapToGlobal(QPoint(0, self.height())))

    def set_theme(self):
        self.combobox.view().parentWidget().setStyleSheet(
            f"background-color: {self.colors.secondary}"
        )
