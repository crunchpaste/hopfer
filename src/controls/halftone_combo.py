from PySide6.QtCore import QPoint, QSize, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QLabel,
    QListView,
    QStyledItemDelegate,
    QVBoxLayout,
    QWidget,
    QFrame
)


class StyledSeparatorDelegate(QStyledItemDelegate):
    def __init__(self, colors, parent=None):
        super().__init__(parent)
        self.colors = colors
    def paint(self, painter, option, index):
        """Paint method to style separators."""
        if index.data(Qt.UserRole) == "separator":  # Check if separator
            painter.save()
            pen = painter.pen()
            pen.setColor(QColor(self.colors.separator))
            pen.setWidth(3)
            painter.setPen(pen)
            painter.drawLine(
                option.rect.left() + 3,
                option.rect.center().y(),
                option.rect.right() - 3,
                option.rect.center().y(),
            )
            painter.restore()
        else:
            super().paint(painter, option, index)

    def sizeHint(self, option, index):
        """Size method to make separators shorter."""
        if index.data(Qt.UserRole) == "separator":
            return QSize(option.rect.width(), 10)  # Set separator height to 8px
        return super().sizeHint(option, index)  # Default height for other items


class HalftoneCombo(QWidget):
    algorithmChanged = Signal(str)  # Signal emitted when the algorithm changes

    def __init__(self, colors):
        super().__init__()

        # Initialize UI components
        self.colors = colors
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
        # it seems that some custom margins are needed for some reason
        self.layout.setContentsMargins(7, 10, 7, 10)
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
        combobox.setView(QListView())  # Enable custom delegate support
        combobox.setItemDelegate(StyledSeparatorDelegate(self.colors, parent=combobox))
        combobox.setMaxVisibleItems(25)
        algorithms = [
            "None",
            # Thresholds
            "Fixed threshold",
            "Niblack threshold",
            "Sauvola threshold",
            "Phansalkar threshold",
            # Random dithers
            "Mezzotint uniform",
            "Mezzotint normal",
            "Mezzotint beta",
            # Ordered dithers
            "Clustered dot",
            "Bayer",
            # Error diffusions
            "Floyd-Steinberg",
            "False Floyd-Steinberg",
            "Jarvis",
            "Stucki",
            "Stucki small",
            "Stucki large",
            "Atkinson",
            "Burkes",
            "Sierra",
            "Sierra2",
            "Sierra2 4A",
            "Nakano",
            # Variable error diffusion
            "Ostromoukhov",
            "Zhou-Fang",
            # EDODF
            "Levien",
        ]
        combobox.addItems(algorithms)

        # Probably the separators could be done in a for loop
        # separator after None
        combobox.insertItem(1, "")
        combobox.setItemData(1, "separator", Qt.UserRole)
        combobox.setItemData(1, 0, Qt.UserRole - 1)  # non-selectable

        # separator after the thresholds
        combobox.insertItem(6, "")
        combobox.setItemData(6, "separator", Qt.UserRole)
        combobox.setItemData(6, 0, Qt.UserRole - 1)  # non-selectable

        # separator after the mezzotints
        combobox.insertItem(10, "")
        combobox.setItemData(10, "separator", Qt.UserRole)
        combobox.setItemData(10, 0, Qt.UserRole - 1)  # non-selectable

        # separator after the ordered dithers
        combobox.insertItem(13, "")
        combobox.setItemData(13, "separator", Qt.UserRole)
        combobox.setItemData(13, 0, Qt.UserRole - 1)  # non-selectable

        # separator after the error diffusions
        combobox.insertItem(26, "")
        combobox.setItemData(26, "separator", Qt.UserRole)
        combobox.setItemData(26, 0, Qt.UserRole - 1)  # non-selectable

        # separator after the VEDs
        combobox.insertItem(29, "")
        combobox.setItemData(29, "separator", Qt.UserRole)
        combobox.setItemData(29, 0, Qt.UserRole - 1)  # non-selectable

        return combobox

    def emit_algorithm_changed(self, text):
        """Emit the algorithmChanged signal with the selected algorithm."""
        self.algorithmChanged.emit(text)

    def showPopup(self):
        """Found this suggested somewhere on stackexchange. Doesn't really seem to work."""
        super().showPopup()
        # Move the popup to the top left of the combobox to control position
        self.view().window().move(self.mapToGlobal(QPoint(0, self.height())))
        
    def set_theme(self):
        self.combobox.view().parentWidget().setStyleSheet(f'background-color: {self.colors.secondary}')
