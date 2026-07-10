import numpy as np

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from acoustics.csv_driver_importer import CsvDriverImporter
from acoustics.driver import Driver
from acoustics.driver_database import DriverDatabase
from acoustics.sealed_box import SealedBox
from gui.add_driver_dialog import AddDriverDialog
from gui.mpl_canvas import MplCanvas


class MainWindow(QMainWindow):
    """Main OpenAcoustics application window."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("OpenAcoustics")
        self.resize(1200, 800)

        self.database = DriverDatabase()
        self.drivers: list[Driver] = self.database.load_all()

        self.frequencies_hz = np.logspace(
            np.log10(10.0),
            np.log10(1000.0),
            1000,
        )

        self.create_menu()
        self.create_widgets()
        self.create_layout()
        self.connect_signals()
        self.reload_driver_selector()

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

    def create_widgets(self) -> None:
        """Create the widgets used by the main window."""
        self.driver_selector_label = QLabel("Driver")
        self.driver_selector = QComboBox()

        self.volume_label = QLabel("Box volume: 10.0 L")
        self.fc_label = QLabel("Fc: --")
        self.qtc_label = QLabel("Qtc: --")
        self.f3_label = QLabel("F3: --")

        self.volume_slider = QSlider(
            Qt.Orientation.Horizontal
        )

        # Slider values represent tenths of a litre.
        self.volume_slider.setMinimum(20)
        self.volume_slider.setMaximum(400)
        self.volume_slider.setValue(100)
        self.volume_slider.setSingleStep(1)

        self.canvas = MplCanvas()

    def create_layout(self) -> None:
        """Create and assign the central window layout."""
        layout = QVBoxLayout()

        layout.addWidget(self.driver_selector_label)
        layout.addWidget(self.driver_selector)
        layout.addWidget(self.volume_label)
        layout.addWidget(self.volume_slider)
        layout.addWidget(self.fc_label)
        layout.addWidget(self.qtc_label)
        layout.addWidget(self.f3_label)
        layout.addWidget(self.canvas)

        central_widget = QWidget()
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

    def connect_signals(self) -> None:
        """Connect GUI events to their handler methods."""
        self.volume_slider.valueChanged.connect(
            self.update_simulation
        )

        self.driver_selector.currentIndexChanged.connect(
            self.update_simulation
        )

    def get_selected_driver(self) -> Driver | None:
        """Return the driver currently selected in the combo box."""
        selected_index = self.driver_selector.currentIndex()

        if selected_index < 0:
            return None

        if selected_index >= len(self.drivers):
            return None

        return self.drivers[selected_index]

    def show_empty_database_message(self) -> None:
        """Tell the user that no drivers exist in the database."""
        self.driver_selector.setEnabled(False)
        self.volume_slider.setEnabled(False)

        self.fc_label.setText("Fc: no driver")
        self.qtc_label.setText("Qtc: no driver")
        self.f3_label.setText("F3: no driver")

        self.canvas.axes.clear()
        self.canvas.axes.set_title(
            "No driver selected"
        )
        self.canvas.draw_idle()

        QMessageBox.information(
            self,
            "Driver database empty",
            (
                "No drivers were found in the OpenAcoustics "
                "database.\n\n"
                "Use Driver → Add Driver or "
                "Driver → Import Drivers from CSV."
            ),
        )

    def open_add_driver_dialog(self) -> None:
        """Open the manual driver-entry dialog."""
        dialog = AddDriverDialog(self)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return

        driver = dialog.get_driver()
        self.database.add_driver(driver)

        self.reload_driver_selector(
            selected_manufacturer=driver.manufacturer,
            selected_model=driver.model,
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

        self.reload_driver_selector()

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

    def reload_driver_selector(
        self,
        selected_manufacturer: str | None = None,
        selected_model: str | None = None,
    ) -> None:
        """Reload the driver selector from the SQLite database."""
        self.drivers = self.database.load_all()

        self.driver_selector.blockSignals(True)
        self.driver_selector.clear()

        selected_index = 0

        for index, driver in enumerate(self.drivers):
            display_name = (
                f"{driver.manufacturer} {driver.model}"
            )
            self.driver_selector.addItem(display_name)

            if (
                driver.manufacturer == selected_manufacturer
                and driver.model == selected_model
            ):
                selected_index = index

        self.driver_selector.blockSignals(False)

        if not self.drivers:
            self.show_empty_database_message()
            return

        self.driver_selector.setEnabled(True)
        self.volume_slider.setEnabled(True)
        self.driver_selector.setCurrentIndex(selected_index)
        self.update_simulation()

    def update_simulation(self, *_args) -> None:
        """Recalculate and redraw the selected driver simulation."""
        driver = self.get_selected_driver()

        if driver is None:
            return

        volume_l = self.volume_slider.value() / 10.0

        try:
            simulation = SealedBox(
                driver=driver,
                volume_l=volume_l,
            )
            simulation.calculate()

            magnitude_db = (
                simulation.calculate_transfer_function(
                    self.frequencies_hz
                )
            )

        except Exception as error:
            QMessageBox.critical(
                self,
                "Simulation error",
                str(error),
            )
            return

        self.volume_label.setText(
            f"Box volume: {volume_l:.1f} L"
        )

        self.fc_label.setText(
            f"Fc: {simulation.fc_hz:.2f} Hz"
        )

        self.qtc_label.setText(
            f"Qtc: {simulation.qtc:.3f}"
        )

        self.f3_label.setText(
            f"F3: {simulation.f3_hz:.2f} Hz"
        )

        axes = self.canvas.axes
        axes.clear()

        axes.semilogx(
            self.frequencies_hz,
            magnitude_db,
            label=(
                f"{driver.manufacturer} "
                f"{driver.model}"
            ),
        )

        axes.axhline(
            -3.0,
            linestyle="--",
            linewidth=1,
        )

        axes.axhline(
            0.0,
            linestyle=":",
            linewidth=1,
        )

        axes.axvline(
            simulation.fc_hz,
            linestyle=":",
            linewidth=1,
            label=f"Fc = {simulation.fc_hz:.1f} Hz",
        )

        axes.axvline(
            simulation.f3_hz,
            linestyle="--",
            linewidth=1,
            label=f"F3 = {simulation.f3_hz:.1f} Hz",
        )

        axes.set_xlabel("Frequency (Hz)")
        axes.set_ylabel(
            "Transfer function magnitude (dB)"
        )

        axes.set_title(
            f"{driver.manufacturer} {driver.model}\n"
            f"Sealed box — {volume_l:.1f} L"
        )

        axes.set_xlim(10.0, 1000.0)
        axes.set_ylim(-30.0, 6.0)
        axes.grid(True, which="both")
        axes.legend()

        self.canvas.figure.tight_layout()
        self.canvas.draw_idle()