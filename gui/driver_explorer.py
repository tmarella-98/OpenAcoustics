from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from acoustics.driver import Driver
from acoustics.driver_database import DriverDatabase
from core.project import Project


class DriverExplorer(QWidget):
    """Browse drivers and assign the selected driver to a project."""

    driver_changed = Signal()

    def __init__(
        self,
        project: Project,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.project = project
        self.database = DriverDatabase()

        self.drivers: list[Driver] = []
        self.filtered_drivers: list[Driver] = []

        self.create_widgets()
        self.create_layout()
        self.connect_signals()
        self.reload_drivers()

    def create_widgets(self) -> None:
        """Create Driver Explorer widgets."""
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search manufacturer or model..."
        )
        self.search_input.setClearButtonEnabled(True)

        self.driver_list = QListWidget()
        self.driver_list.setMinimumWidth(220)

        self.parameter_table = QTableWidget()
        self.parameter_table.setColumnCount(2)
        self.parameter_table.setHorizontalHeaderLabels(
            ["Parameter", "Value"]
        )

        self.parameter_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )

        self.parameter_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )

        self.parameter_table.verticalHeader().setVisible(False)

        self.parameter_table.horizontalHeader().setStretchLastSection(
            True
        )

        self.cad_drawing_label = QLabel(
            "No CAD drawing available"
        )

        self.cad_drawing_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.cad_drawing_label.setMinimumHeight(260)

        self.cad_drawing_label.setStyleSheet(
            """
            QLabel {
                border: 1px solid gray;
                padding: 8px;
            }
            """
        )

    def create_layout(self) -> None:
        """Create the Driver Explorer layout."""
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.search_input)
        left_layout.addWidget(self.driver_list)

        left_widget = QWidget()
        left_widget.setLayout(left_layout)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.cad_drawing_label)
        right_layout.addWidget(self.parameter_table)

        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout = QHBoxLayout()
        layout.addWidget(splitter)

        self.setLayout(layout)

    def connect_signals(self) -> None:
        """Connect Driver Explorer signals."""
        self.search_input.textChanged.connect(
            self.filter_drivers
        )

        self.driver_list.currentRowChanged.connect(
            self.show_selected_driver
        )

    def set_project(
        self,
        project: Project,
    ) -> None:
        """Replace the active project."""
        self.project = project

        selected_driver = project.driver

        if selected_driver is None:
            self.driver_list.blockSignals(True)
            self.driver_list.clearSelection()
            self.driver_list.setCurrentRow(-1)
            self.driver_list.blockSignals(False)

            self.parameter_table.setRowCount(0)
            self.clear_cad_drawing()
            return

        matching_index = self.find_driver_index(
            selected_driver
        )

        if matching_index is None:
            self.parameter_table.setRowCount(0)
            self.clear_cad_drawing(
                "Project driver is not in the local database"
            )
            return

        self.driver_list.setCurrentRow(
            matching_index
        )

        self.show_selected_driver(
            matching_index
        )

    def reload_drivers(self) -> None:
        """Reload all drivers from the SQLite database."""
        current_driver = self.project.driver

        self.drivers = self.database.load_all()

        self.filter_drivers(
            self.search_input.text()
        )

        if current_driver is not None:
            matching_index = self.find_driver_index(
                current_driver
            )

            if matching_index is not None:
                self.driver_list.setCurrentRow(
                    matching_index
                )
                self.show_selected_driver(
                    matching_index
                )

    def filter_drivers(
        self,
        search_text: str,
    ) -> None:
        """Filter drivers by manufacturer or model."""
        search_text = search_text.strip().lower()

        if not search_text:
            self.filtered_drivers = list(
                self.drivers
            )
        else:
            self.filtered_drivers = [
                driver
                for driver in self.drivers
                if search_text
                in (
                    f"{driver.manufacturer} "
                    f"{driver.model}"
                ).lower()
            ]

        current_project_driver = self.project.driver

        self.driver_list.blockSignals(True)
        self.driver_list.clear()

        for driver in self.filtered_drivers:
            self.driver_list.addItem(
                f"{driver.manufacturer} "
                f"{driver.model}"
            )

        self.driver_list.blockSignals(False)

        if not self.filtered_drivers:
            self.parameter_table.setRowCount(0)
            self.clear_cad_drawing(
                "No matching drivers"
            )
            return

        selected_index = 0

        if current_project_driver is not None:
            matching_index = self.find_driver_index(
                current_project_driver
            )

            if matching_index is not None:
                selected_index = matching_index

        self.driver_list.setCurrentRow(
            selected_index
        )

        self.show_selected_driver(
            selected_index
        )

    def find_driver_index(
        self,
        selected_driver: Driver,
    ) -> int | None:
        """Find a driver in the filtered driver collection."""
        for index, driver in enumerate(
            self.filtered_drivers
        ):
            if (
                driver.manufacturer
                == selected_driver.manufacturer
                and driver.model
                == selected_driver.model
            ):
                return index

        return None

    def show_selected_driver(
        self,
        row: int,
    ) -> None:
        """Display and assign the selected driver."""
        if (
            row < 0
            or row >= len(self.filtered_drivers)
        ):
            self.parameter_table.setRowCount(0)
            self.clear_cad_drawing()
            return

        driver = self.filtered_drivers[row]

        self.project.set_driver(driver)

        self.populate_driver_table(driver)
        self.update_cad_drawing(driver)

        self.driver_changed.emit()

    def populate_driver_table(
        self,
        driver: Driver,
    ) -> None:
        """Populate the parameter table for one driver."""
        parameters = [
            ("Manufacturer", driver.manufacturer, ""),
            ("Model", driver.model, ""),
            ("Fs", driver.fs, "Hz"),
            ("Qts", driver.qts, ""),
            ("Qes", driver.qes, ""),
            ("Qms", driver.qms, ""),
            ("Vas", driver.vas, "L"),
            ("Re", driver.re, "Ω"),
            ("Le", driver.le, "mH"),
            ("Sd", driver.sd, "cm²"),
            ("Xmax", driver.xmax, "mm"),
            ("BL", driver.bl, "N/A"),
            ("Mms", driver.mms, "g"),
            ("Cms", driver.cms, "mm/N"),
        ]

        self.parameter_table.setRowCount(
            len(parameters)
        )

        for row, (name, value, unit) in enumerate(
            parameters
        ):
            name_item = QTableWidgetItem(name)

            value_item = QTableWidgetItem(
                self.format_value(
                    value,
                    unit,
                )
            )

            self.parameter_table.setItem(
                row,
                0,
                name_item,
            )

            self.parameter_table.setItem(
                row,
                1,
                value_item,
            )

        self.parameter_table.resizeColumnsToContents()

    def update_cad_drawing(
        self,
        driver: Driver,
    ) -> None:
        """Load the driver's local CAD drawing when available."""
        cad_path = getattr(
            driver,
            "cad_drawing_path",
            None,
        )

        if not cad_path:
            self.clear_cad_drawing()
            return

        path = Path(cad_path)

        if not path.exists():
            self.clear_cad_drawing(
                "CAD drawing file not found"
            )
            return

        pixmap = QPixmap(str(path))

        if pixmap.isNull():
            self.clear_cad_drawing(
                "Could not load CAD drawing"
            )
            return

        target_size = self.cad_drawing_label.size()

        scaled_pixmap = pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.cad_drawing_label.setText("")
        self.cad_drawing_label.setPixmap(
            scaled_pixmap
        )

    def clear_cad_drawing(
        self,
        message: str = "No CAD drawing available",
    ) -> None:
        """Clear the CAD drawing panel."""
        self.cad_drawing_label.setPixmap(
            QPixmap()
        )
        self.cad_drawing_label.setText(
            message
        )

    @staticmethod
    def format_value(
        value: str | float | int | None,
        unit: str,
    ) -> str:
        """Format stored values for display."""
        if value is None:
            return "N/A"

        if isinstance(value, float):
            value_text = f"{value:g}"
        else:
            value_text = str(value)

        if unit:
            return f"{value_text} {unit}"

        return value_text