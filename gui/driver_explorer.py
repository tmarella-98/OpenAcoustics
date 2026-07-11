from pathlib import Path

from PySide6.QtCore import Qt
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
    """Browse drivers and inspect their stored parameters."""

    def __init__(
        self,
        project: Project,
    ):
        super().__init__()

        self.project = project
        

        self.database = DriverDatabase()
        self.drivers: list[Driver] = []
        self.filtered_drivers: list[Driver] = []

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(
            "Search manufacturer or model..."
        )

        self.driver_list = QListWidget()

        self.parameter_table = QTableWidget()
        self.parameter_table.setColumnCount(2)
        self.parameter_table.setHorizontalHeaderLabels(
            ["Parameter", "Value"]
        )
        self.parameter_table.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        self.parameter_table.verticalHeader().setVisible(False)
        self.parameter_table.horizontalHeader().setStretchLastSection(True)

        self.cad_drawing_label = QLabel(
            "No CAD drawing available"
        )
        self.cad_drawing_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )
        self.cad_drawing_label.setMinimumHeight(260)
        self.cad_drawing_label.setStyleSheet(
            "border: 1px solid gray;"
        )

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

        self.search_input.textChanged.connect(
            self.filter_drivers
        )

        self.driver_list.currentRowChanged.connect(
            self.show_selected_driver
        )

        self.reload_drivers()

    def reload_drivers(self) -> None:
        """Reload all drivers from the database."""
        self.drivers = self.database.load_all()
        self.filter_drivers(
            self.search_input.text()
        )

    def filter_drivers(self, search_text: str) -> None:
        """Filter drivers by manufacturer or model."""
        search_text = search_text.strip().lower()

        if not search_text:
            self.filtered_drivers = list(self.drivers)
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

        self.driver_list.blockSignals(True)
        self.driver_list.clear()

        for driver in self.filtered_drivers:
            self.driver_list.addItem(
                f"{driver.manufacturer} {driver.model}"
            )

        self.driver_list.blockSignals(False)

        if self.filtered_drivers:
            self.driver_list.setCurrentRow(0)
            self.show_selected_driver(0)
        else:
            self.parameter_table.setRowCount(0)
            self.clear_cad_drawing()

    def show_selected_driver(self, row: int) -> None:
        """Show the selected driver's information."""
        if row < 0 or row >= len(self.filtered_drivers):
            self.parameter_table.setRowCount(0)
            self.clear_cad_drawing()
            return

        driver = self.filtered_drivers[row]

        self.populate_driver_table(driver)
        self.update_cad_drawing(driver)

    def populate_driver_table(
        self,
        driver: Driver,
    ) -> None:
        """Populate the parameter table."""
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
            self.parameter_table.setItem(
                row,
                0,
                QTableWidgetItem(name),
            )

            self.parameter_table.setItem(
                row,
                1,
                QTableWidgetItem(
                    self.format_value(value, unit)
                ),
            )

        self.parameter_table.resizeColumnsToContents()

    def update_cad_drawing(
        self,
        driver: Driver,
    ) -> None:
        """
        Load a local CAD drawing if the Driver object has
        a cad_drawing_path attribute.
        """
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

        scaled_pixmap = pixmap.scaled(
            self.cad_drawing_label.size(),
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
        self.cad_drawing_label.setText(message)

    @staticmethod
    def format_value(
        value: str | float | None,
        unit: str,
    ) -> str:
        """Format values for display."""
        if value is None:
            return "N/A"

        if isinstance(value, float):
            value_text = f"{value:g}"
        else:
            value_text = str(value)

        if unit:
            return f"{value_text} {unit}"

        return value_text