from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QListWidget,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from acoustics.driver import Driver
from acoustics.driver_database import DriverDatabase


class DriverExplorer(QWidget):
    """Browse drivers and inspect their stored parameters."""

    def __init__(self) -> None:
        super().__init__()

        self.database = DriverDatabase()
        self.drivers: list[Driver] = []

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

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.driver_list)
        splitter.addWidget(self.parameter_table)

        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        layout = QHBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)

        self.driver_list.currentRowChanged.connect(
            self.show_selected_driver
        )

        self.reload_drivers()

    def reload_drivers(self) -> None:
        """Reload all drivers from the SQLite database."""
        self.drivers = self.database.load_all()

        self.driver_list.blockSignals(True)
        self.driver_list.clear()

        for driver in self.drivers:
            self.driver_list.addItem(
                f"{driver.manufacturer} {driver.model}"
            )

        self.driver_list.blockSignals(False)

        if self.drivers:
            self.driver_list.setCurrentRow(0)
            self.show_selected_driver(0)
        else:
            self.parameter_table.setRowCount(0)

    def show_selected_driver(self, row: int) -> None:
        """Show the selected driver's parameters."""
        if row < 0 or row >= len(self.drivers):
            self.parameter_table.setRowCount(0)
            return

        driver = self.drivers[row]
        self.populate_driver_table(driver)

    def populate_driver_table(self, driver: Driver) -> None:
        """Populate the details table for one driver."""
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

        self.parameter_table.setRowCount(len(parameters))

        for row, (name, value, unit) in enumerate(parameters):
            name_item = QTableWidgetItem(name)
            value_item = QTableWidgetItem(
                self.format_value(value, unit)
            )

            self.parameter_table.setItem(row, 0, name_item)
            self.parameter_table.setItem(row, 1, value_item)

        self.parameter_table.resizeColumnsToContents()

    @staticmethod
    def format_value(
        value: str | float | None,
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