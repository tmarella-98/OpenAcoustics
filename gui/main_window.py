from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QInputDialog,
    QMainWindow,
    QMessageBox,
    QSplitter,
)

from acoustics.csv_driver_importer import (
    CsvDriverImporter,
)
from acoustics.driver_database import (
    DriverDatabase,
)
from core.project import Project
from gui.add_driver_dialog import (
    AddDriverDialog,
)
from gui.driver_explorer import (
    DriverExplorer,
)
from gui.simulation_workspace import (
    SimulationWorkspace,
)


class MainWindow(QMainWindow):
    """Main OpenAcoustics application window."""

    def __init__(self) -> None:
        super().__init__()

        self.project = Project(
            name="Untitled Project"
        )

        self.project_file_path: str | None = None
        self.database = DriverDatabase()

        self.resize(1500, 900)

        self.create_menu()
        self.create_workspace()
        self.update_window_title()

    def create_menu(self) -> None:
        """Create the application menu bar."""
        file_menu = self.menuBar().addMenu(
            "File"
        )

        driver_menu = self.menuBar().addMenu(
            "Driver"
        )

        new_project_action = QAction(
            "New Project",
            self,
        )
        new_project_action.setShortcut(
            "Ctrl+N"
        )
        new_project_action.triggered.connect(
            self.new_project
        )

        open_project_action = QAction(
            "Open Project...",
            self,
        )
        open_project_action.setShortcut(
            "Ctrl+O"
        )
        open_project_action.triggered.connect(
            self.open_project
        )

        save_project_action = QAction(
            "Save Project",
            self,
        )
        save_project_action.setShortcut(
            "Ctrl+S"
        )
        save_project_action.triggered.connect(
            self.save_project
        )

        save_project_as_action = QAction(
            "Save Project As...",
            self,
        )
        save_project_as_action.setShortcut(
            "Ctrl+Shift+S"
        )
        save_project_as_action.triggered.connect(
            self.save_project_as
        )

        exit_action = QAction(
            "Exit",
            self,
        )
        exit_action.triggered.connect(
            self.close
        )

        file_menu.addAction(
            new_project_action
        )
        file_menu.addAction(
            open_project_action
        )
        file_menu.addSeparator()
        file_menu.addAction(
            save_project_action
        )
        file_menu.addAction(
            save_project_as_action
        )
        file_menu.addSeparator()
        file_menu.addAction(
            exit_action
        )

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

        driver_menu.addAction(
            add_driver_action
        )
        driver_menu.addAction(
            import_csv_action
        )

    def create_workspace(self) -> None:
        """Create the main engineering workspace."""
        self.driver_explorer = DriverExplorer(
            project=self.project
        )

        self.simulation_workspace = (
            SimulationWorkspace(
                project=self.project
            )
        )

        self.driver_explorer.driver_changed.connect(
            self.simulation_workspace.update_simulation
        )

        self.workspace_splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        self.workspace_splitter.addWidget(
            self.driver_explorer
        )

        self.workspace_splitter.addWidget(
            self.simulation_workspace
        )

        self.workspace_splitter.setStretchFactor(
            0,
            1,
        )

        self.workspace_splitter.setStretchFactor(
            1,
            2,
        )

        self.workspace_splitter.setSizes(
            [500, 1000]
        )

        self.setCentralWidget(
            self.workspace_splitter
        )

    def new_project(self) -> None:
        """Create a new project."""
        project_name, accepted = (
            QInputDialog.getText(
                self,
                "New Project",
                "Project name:",
                text="Untitled Project",
            )
        )

        if not accepted:
            return

        project_name = project_name.strip()

        if not project_name:
            project_name = "Untitled Project"

        self.project = Project(
            name=project_name
        )

        self.project_file_path = None

        self.driver_explorer.set_project(
            self.project
        )

        self.simulation_workspace.set_project(
            self.project
        )

        self.update_window_title()

    def open_project(self) -> None:
        """Open an existing OpenAcoustics project."""
        file_path, _selected_filter = (
            QFileDialog.getOpenFileName(
                self,
                "Open OpenAcoustics Project",
                "",
                (
                    "OpenAcoustics projects "
                    "(*.oa-project);;"
                    "All files (*.*)"
                ),
            )
        )

        if not file_path:
            return

        try:
            project = Project.load(
                file_path
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Could not open project",
                str(error),
            )
            return

        self.project = project
        self.project_file_path = file_path

        self.driver_explorer.set_project(
            self.project
        )

        self.simulation_workspace.set_project(
            self.project
        )

        self.update_window_title()

    def save_project(self) -> None:
        """Save the current project."""
        if self.project_file_path is None:
            self.save_project_as()
            return

        try:
            self.project.save(
                self.project_file_path
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Could not save project",
                str(error),
            )
            return

        self.update_window_title()

    def save_project_as(self) -> None:
        """Save the project using a selected file path."""
        suggested_name = (
            f"{self.project.name}.oa-project"
        )

        file_path, _selected_filter = (
            QFileDialog.getSaveFileName(
                self,
                "Save OpenAcoustics Project",
                suggested_name,
                (
                    "OpenAcoustics projects "
                    "(*.oa-project);;"
                    "All files (*.*)"
                ),
            )
        )

        if not file_path:
            return

        if not file_path.lower().endswith(
            ".oa-project"
        ):
            file_path += ".oa-project"

        try:
            self.project.save(file_path)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Could not save project",
                str(error),
            )
            return

        self.project_file_path = file_path

        self.update_window_title()

    def open_add_driver_dialog(self) -> None:
        """Open the manual driver-entry dialog."""
        dialog = AddDriverDialog(self)

        if (
            dialog.exec()
            != QDialog.DialogCode.Accepted
        ):
            return

        driver = dialog.get_driver()

        try:
            self.database.add_driver(driver)

        except Exception as error:
            QMessageBox.critical(
                self,
                "Could not add driver",
                str(error),
            )
            return

        self.refresh_driver_explorer()

        QMessageBox.information(
            self,
            "Driver added",
            (
                f"{driver.manufacturer} "
                f"{driver.model} "
                "was added successfully."
            ),
        )

    def import_drivers_from_csv(self) -> None:
        """Import driver records from a CSV file."""
        file_path, _selected_filter = (
            QFileDialog.getOpenFileName(
                self,
                "Import Driver CSV",
                "",
                "CSV files (*.csv);;"
                "All files (*.*)",
            )
        )

        if not file_path:
            return

        importer = CsvDriverImporter(
            database=self.database
        )

        try:
            result = importer.import_file(
                file_path
            )

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
                remaining = (
                    len(result.errors) - 10
                )

                message += (
                    f"\n...and {remaining} "
                    "more errors."
                )

        QMessageBox.information(
            self,
            "CSV import complete",
            message,
        )

    def refresh_driver_explorer(self) -> None:
        """Reload the Driver Explorer."""
        self.driver_explorer.reload_drivers()

    def update_window_title(self) -> None:
        """Update the main window title."""
        self.setWindowTitle(
            f"{self.project.name} "
            "— OpenAcoustics"
        )

    def closeEvent(self, event) -> None:
        """Ask whether the project should be saved before closing."""
        response = QMessageBox.question(
            self,
            "Close OpenAcoustics",
            "Save the current project before closing?",
            (
                QMessageBox.StandardButton.Yes
                | QMessageBox.StandardButton.No
                | QMessageBox.StandardButton.Cancel
            ),
        )

        if (
            response
            == QMessageBox.StandardButton.Cancel
        ):
            event.ignore()
            return

        if (
            response
            == QMessageBox.StandardButton.Yes
        ):
            self.save_project()

            if self.project_file_path is None:
                event.ignore()
                return

        event.accept()