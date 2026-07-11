from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QMainWindow,
    QMessageBox,
)

from acoustics.csv_driver_importer import CsvDriverImporter
from acoustics.driver_database import DriverDatabase
from gui.add_driver_dialog import AddDriverDialog
from gui.driver_explorer import DriverExplorer


class MainWindow(QMainWindow):
    """Main OpenAcoustics application window."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("OpenAcoustics")
        self.resize(1200, 800)

        self.database = DriverDatabase()

        self.create_menu()
        self.create_driver_explorer()

    def create_menu(self) -> None:
        """Create the application menu bar."""
        driver_menu = self.menuBar().addMenu("Driver")

        add_driver_action = QAction(
            "Add Driver",
            self,
        )
        add_driver_action.triggered.connect(
            self.open_add_driver_dialog
        )

        import_csv_action = QAction(
            "Import Drivers from CSV",
            self,
        )
        import_csv_action.triggered.connect(
            self.import_drivers_from_csv
        )

        driver_menu.addAction(add_driver_action)
        driver_menu.addAction(import_csv_action)

    def create_driver_explorer(self) -> None:
        """Create and display the Driver Explorer."""
        self.driver_explorer = DriverExplorer()

        self.setCentralWidget(
            self.driver_explorer
        )

    def open_add_driver_dialog(self) -> None:
        """Open the manual driver-entry dialog."""
        dialog = AddDriverDialog(self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        driver = dialog.get_driver()
        self.database.add_driver(driver)

        self.refresh_driver_explorer()

        QMessageBox.information(
            self,
            "Driver added",
            (
                f"{driver.manufacturer} "
                f"{driver.model} was added successfully."
            ),
        )

    def import_drivers_from_csv(self) -> None:
        """Select a CSV file and import its drivers."""
        file_path, _selected_filter = QFileDialog.getOpenFileName(
            self,
            "Import Driver CSV",
            "",
            "CSV files (*.csv);;All files (*.*)",
        )

        if not file_path:
            return

        importer = CsvDriverImporter(
            database=self.database
        )

        try:
            result = importer.import_file(file_path)

        except Exception as error:
            QMessageBox.critical(
                self,
                "CSV import failed",
                str(error),
            )
            return

        self.refresh_driver_explorer()

        message = (
            f"Imported: {result.imported_count}\n"
            f"Failed: {result.failed_count}"
        )

        if result.errors:
            error_preview = "\n".join(
                result.errors[:10]
            )

            message += (
                "\n\nErrors:\n"
                f"{error_preview}"
            )

            if len(result.errors) > 10:
                remaining = len(result.errors) - 10

                message += (
                    f"\n...and {remaining} more errors."
                )

        QMessageBox.information(
            self,
            "CSV import complete",
            message,
        )

    def refresh_driver_explorer(self) -> None:
        """Reload the Driver Explorer after database changes."""
        self.driver_explorer.reload_drivers()

        self.driver_explorer = DriverExplorer()
        self.setCentralWidget(self.driver_explorer)

        old_widget.deleteLater()