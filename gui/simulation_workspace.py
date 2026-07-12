import numpy as np

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from acoustics.bass_reflex import BassReflex
from acoustics.sealed_box import SealedBox
from core.enclosures.bass_reflex import BassReflexEnclosure
from core.enclosures.sealed import SealedEnclosure
from core.project import Project
from gui.mpl_canvas import MplCanvas


class SimulationWorkspace(QWidget):
    """Workspace for enclosure controls, simulation results and plots."""

    def __init__(
        self,
        project: Project,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.project = project

        self.frequencies_hz = np.logspace(
            np.log10(10.0),
            np.log10(1000.0),
            1200,
        )

        self._updating_controls = False

        self.create_widgets()
        self.create_layout()
        self.connect_signals()
        self.set_project(project)

    def create_widgets(self) -> None:
        """Create workspace controls and result widgets."""
        self.simulation_type_selector = QComboBox()
        self.simulation_type_selector.addItem(
            "Sealed Box",
            "sealed",
        )
        self.simulation_type_selector.addItem(
            "Bass Reflex",
            "bass_reflex",
        )

        self.volume_spinbox = QDoubleSpinBox()
        self.volume_spinbox.setRange(0.1, 1000.0)
        self.volume_spinbox.setDecimals(1)
        self.volume_spinbox.setSingleStep(0.1)
        self.volume_spinbox.setSuffix(" L")
        self.volume_spinbox.setValue(10.0)
        self.volume_spinbox.setKeyboardTracking(False)

        self.volume_slider = QSlider(
            Qt.Orientation.Horizontal
        )
        self.volume_slider.setMinimum(1)
        self.volume_slider.setMaximum(1000)
        self.volume_slider.setValue(100)
        self.volume_slider.setSingleStep(1)

        self.tuning_spinbox = QDoubleSpinBox()
        self.tuning_spinbox.setRange(5.0, 500.0)
        self.tuning_spinbox.setDecimals(1)
        self.tuning_spinbox.setSingleStep(0.5)
        self.tuning_spinbox.setSuffix(" Hz")
        self.tuning_spinbox.setValue(38.0)
        self.tuning_spinbox.setKeyboardTracking(False)

        self.port_diameter_spinbox = QDoubleSpinBox()
        self.port_diameter_spinbox.setRange(1.0, 1000.0)
        self.port_diameter_spinbox.setDecimals(1)
        self.port_diameter_spinbox.setSingleStep(1.0)
        self.port_diameter_spinbox.setSuffix(" mm")
        self.port_diameter_spinbox.setValue(68.0)
        self.port_diameter_spinbox.setKeyboardTracking(False)

        self.driver_label = QLabel("Driver: None")
        self.fc_label = QLabel("Fc: N/A")
        self.qtc_label = QLabel("Qtc: N/A")
        self.f3_label = QLabel("F3: N/A")
        self.fb_label = QLabel("Fb: N/A")

        self.status_label = QLabel(
            "Select a driver to begin."
        )
        self.status_label.setWordWrap(True)

        self.canvas = MplCanvas(
            width=8.0,
            height=5.0,
            dpi=100,
        )

    def create_layout(self) -> None:
        """Create the workspace layout."""
        simulation_group = QGroupBox(
            "Simulation"
        )
        simulation_form = QFormLayout()

        simulation_form.addRow(
            "Type",
            self.simulation_type_selector,
        )
        simulation_form.addRow(
            "Box volume",
            self.volume_spinbox,
        )
        simulation_form.addRow(
            "",
            self.volume_slider,
        )
        simulation_form.addRow(
            "Tuning frequency",
            self.tuning_spinbox,
        )
        simulation_form.addRow(
            "Port diameter",
            self.port_diameter_spinbox,
        )

        simulation_group.setLayout(
            simulation_form
        )

        results_group = QGroupBox(
            "Results"
        )
        results_form = QFormLayout()

        results_form.addRow(
            self.driver_label
        )
        results_form.addRow(
            self.fc_label
        )
        results_form.addRow(
            self.qtc_label
        )
        results_form.addRow(
            self.f3_label
        )
        results_form.addRow(
            self.fb_label
        )
        results_form.addRow(
            self.status_label
        )

        results_group.setLayout(
            results_form
        )

        layout = QVBoxLayout()
        layout.addWidget(simulation_group)
        layout.addWidget(results_group)
        layout.addWidget(self.canvas, stretch=1)

        self.setLayout(layout)

    def connect_signals(self) -> None:
        """Connect controls to simulation updates."""
        self.simulation_type_selector.currentIndexChanged.connect(
            self.on_simulation_type_changed
        )

        self.volume_spinbox.valueChanged.connect(
            self.on_volume_spinbox_changed
        )

        self.volume_slider.valueChanged.connect(
            self.on_volume_slider_changed
        )

        self.tuning_spinbox.valueChanged.connect(
            self.update_simulation
        )

        self.port_diameter_spinbox.valueChanged.connect(
            self.update_simulation
        )

    def set_project(
        self,
        project: Project,
    ) -> None:
        """Replace the active project."""
        self.project = project
        self.load_controls_from_project()
        self.update_simulation()

    def load_controls_from_project(self) -> None:
        """Load enclosure settings from the active project."""
        self._updating_controls = True

        try:
            enclosure = self.project.enclosure

            if isinstance(
                enclosure,
                SealedEnclosure,
            ):
                self.simulation_type_selector.setCurrentIndex(
                    self.simulation_type_selector.findData(
                        "sealed"
                    )
                )
                self.set_volume_value(
                    enclosure.volume_l
                )

            elif isinstance(
                enclosure,
                BassReflexEnclosure,
            ):
                self.simulation_type_selector.setCurrentIndex(
                    self.simulation_type_selector.findData(
                        "bass_reflex"
                    )
                )
                self.set_volume_value(
                    enclosure.volume_l
                )
                self.tuning_spinbox.setValue(
                    enclosure.tuning_hz
                )
                self.port_diameter_spinbox.setValue(
                    enclosure.port_diameter_mm
                )

            else:
                self.simulation_type_selector.setCurrentIndex(
                    self.simulation_type_selector.findData(
                        "sealed"
                    )
                )
                self.set_volume_value(10.0)

        finally:
            self._updating_controls = False

        self.update_control_visibility()

    def update_control_visibility(self) -> None:
        """Show controls relevant to the selected simulation type."""
        simulation_type = (
            self.simulation_type_selector.currentData()
        )

        is_bass_reflex = (
            simulation_type == "bass_reflex"
        )

        self.tuning_spinbox.setVisible(
            is_bass_reflex
        )
        self.port_diameter_spinbox.setVisible(
            is_bass_reflex
        )

        form_layout = (
            self.tuning_spinbox.parentWidget().layout()
        )

        if isinstance(
            form_layout,
            QFormLayout,
        ):
            tuning_label = form_layout.labelForField(
                self.tuning_spinbox
            )
            port_label = form_layout.labelForField(
                self.port_diameter_spinbox
            )

            if tuning_label is not None:
                tuning_label.setVisible(
                    is_bass_reflex
                )

            if port_label is not None:
                port_label.setVisible(
                    is_bass_reflex
                )

    def on_simulation_type_changed(
        self,
        *_args,
    ) -> None:
        """Handle a change in enclosure type."""
        if self._updating_controls:
            return

        self.update_control_visibility()
        self.update_simulation()

    def on_volume_spinbox_changed(
        self,
        volume_l: float,
    ) -> None:
        """Keep the slider synchronized with the spinbox."""
        if self._updating_controls:
            return

        self._updating_controls = True

        try:
            slider_value = int(
                round(volume_l * 10.0)
            )
            self.volume_slider.setValue(
                slider_value
            )

        finally:
            self._updating_controls = False

        self.update_simulation()

    def on_volume_slider_changed(
        self,
        slider_value: int,
    ) -> None:
        """Keep the spinbox synchronized with the slider."""
        if self._updating_controls:
            return

        volume_l = slider_value / 10.0

        self._updating_controls = True

        try:
            self.volume_spinbox.setValue(
                volume_l
            )

        finally:
            self._updating_controls = False

        self.update_simulation()

    def set_volume_value(
        self,
        volume_l: float,
    ) -> None:
        """Set volume controls without causing duplicate updates."""
        self.volume_spinbox.setValue(
            volume_l
        )

        slider_value = int(
            round(volume_l * 10.0)
        )

        self.volume_slider.setValue(
            slider_value
        )

    def update_simulation(
        self,
        *_args,
    ) -> None:
        """Update the project, calculate the model and redraw the plot."""
        if self._updating_controls:
            return

        driver = self.project.driver

        if driver is None:
            self.show_no_driver_state()
            return

        self.driver_label.setText(
            "Driver: "
            f"{driver.manufacturer} "
            f"{driver.model}"
        )

        simulation_type = (
            self.simulation_type_selector.currentData()
        )

        try:
            if simulation_type == "sealed":
                self.run_sealed_simulation()

            elif simulation_type == "bass_reflex":
                self.run_bass_reflex_simulation()

            else:
                raise ValueError(
                    "Unsupported simulation type."
                )

        except Exception as error:
            self.show_simulation_error(
                str(error)
            )

    def run_sealed_simulation(self) -> None:
        """Run and display a sealed-box simulation."""
        volume_l = self.volume_spinbox.value()

        enclosure = SealedEnclosure(
            volume_l=volume_l
        )

        self.project.set_enclosure(
            enclosure
        )

        simulation = SealedBox(
            driver=self.project.driver,
            volume_l=volume_l,
        )

        simulation.calculate()

        magnitude_db = (
            simulation.calculate_transfer_function(
                self.frequencies_hz
            )
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

        self.fb_label.setText(
            "Fb: N/A"
        )

        self.status_label.setText(
            "Sealed-box simulation calculated successfully."
        )

        axes = self.canvas.axes
        axes.clear()

        axes.semilogx(
            self.frequencies_hz,
            magnitude_db,
            label=(
                f"Sealed — "
                f"{volume_l:.1f} L"
            ),
        )

        axes.axhline(
            0.0,
            linestyle=":",
            linewidth=1,
        )

        axes.axhline(
            -3.0103,
            linestyle="--",
            linewidth=1,
        )

        axes.axvline(
            simulation.fc_hz,
            linestyle=":",
            linewidth=1,
            label=(
                f"Fc = "
                f"{simulation.fc_hz:.1f} Hz"
            ),
        )

        axes.axvline(
            simulation.f3_hz,
            linestyle="--",
            linewidth=1,
            label=(
                f"F3 = "
                f"{simulation.f3_hz:.1f} Hz"
            ),
        )

        self.finish_plot(
            title=(
                f"{self.project.driver.manufacturer} "
                f"{self.project.driver.model}\n"
                "Sealed-box transfer function"
            ),
            y_min=-30.0,
            y_max=6.0,
        )

    def run_bass_reflex_simulation(self) -> None:
        """Run and display a bass-reflex simulation."""
        volume_l = self.volume_spinbox.value()
        tuning_hz = self.tuning_spinbox.value()
        port_diameter_mm = (
            self.port_diameter_spinbox.value()
        )

        enclosure = BassReflexEnclosure(
            volume_l=volume_l,
            tuning_hz=tuning_hz,
            port_diameter_mm=port_diameter_mm,
            port_count=1,
        )

        self.project.set_enclosure(
            enclosure
        )

        simulation = BassReflex(
            driver=self.project.driver,
            enclosure=enclosure,
        )

        simulation.calculate()

        magnitude_db = (
            simulation.calculate_transfer_function(
                self.frequencies_hz
            )
        )

        self.fc_label.setText(
            "Fc: N/A"
        )

        self.qtc_label.setText(
            "Qtc: N/A"
        )

        self.f3_label.setText(
            f"F3: {simulation.f3_hz:.2f} Hz"
        )

        self.fb_label.setText(
            f"Fb: {tuning_hz:.2f} Hz"
        )

        self.status_label.setText(
            "Bass-reflex simulation calculated successfully."
        )

        axes = self.canvas.axes
        axes.clear()

        axes.semilogx(
            self.frequencies_hz,
            magnitude_db,
            label=(
                f"Bass reflex — "
                f"{volume_l:.1f} L, "
                f"Fb {tuning_hz:.1f} Hz"
            ),
        )

        axes.axhline(
            0.0,
            linestyle=":",
            linewidth=1,
        )

        axes.axhline(
            -3.0103,
            linestyle="--",
            linewidth=1,
        )

        axes.axvline(
            tuning_hz,
            linestyle=":",
            linewidth=1,
            label=f"Fb = {tuning_hz:.1f} Hz",
        )

        axes.axvline(
            simulation.f3_hz,
            linestyle="--",
            linewidth=1,
            label=(
                f"F3 = "
                f"{simulation.f3_hz:.1f} Hz"
            ),
        )

        self.finish_plot(
            title=(
                f"{self.project.driver.manufacturer} "
                f"{self.project.driver.model}\n"
                "Bass-reflex transfer function"
            ),
            y_min=-40.0,
            y_max=10.0,
        )

    def finish_plot(
        self,
        title: str,
        y_min: float,
        y_max: float,
    ) -> None:
        """Apply common plot formatting and redraw the canvas."""
        axes = self.canvas.axes

        axes.set_xlabel(
            "Frequency (Hz)"
        )

        axes.set_ylabel(
            "Transfer function magnitude (dB)"
        )

        axes.set_title(title)
        axes.set_xlim(10.0, 1000.0)
        axes.set_ylim(y_min, y_max)
        axes.grid(
            True,
            which="both",
        )
        axes.legend()

        self.canvas.figure.tight_layout()
        self.canvas.draw_idle()

    def show_no_driver_state(self) -> None:
        """Display an empty state when the project has no driver."""
        self.driver_label.setText(
            "Driver: None"
        )

        self.fc_label.setText(
            "Fc: N/A"
        )

        self.qtc_label.setText(
            "Qtc: N/A"
        )

        self.f3_label.setText(
            "F3: N/A"
        )

        self.fb_label.setText(
            "Fb: N/A"
        )

        self.status_label.setText(
            "Select a driver in the Driver Explorer."
        )

        axes = self.canvas.axes
        axes.clear()
        axes.set_title(
            "No driver selected"
        )
        axes.set_xlabel(
            "Frequency (Hz)"
        )
        axes.set_ylabel(
            "Transfer function magnitude (dB)"
        )
        axes.grid(
            True,
            which="both",
        )

        self.canvas.draw_idle()

    def show_simulation_error(
        self,
        message: str,
    ) -> None:
        """Display a simulation error without crashing the application."""
        self.fc_label.setText(
            "Fc: N/A"
        )
        self.qtc_label.setText(
            "Qtc: N/A"
        )
        self.f3_label.setText(
            "F3: N/A"
        )
        self.fb_label.setText(
            "Fb: N/A"
        )

        self.status_label.setText(
            f"Simulation unavailable: {message}"
        )

        axes = self.canvas.axes
        axes.clear()
        axes.set_title(
            "Simulation unavailable"
        )
        axes.text(
            0.5,
            0.5,
            message,
            horizontalalignment="center",
            verticalalignment="center",
            transform=axes.transAxes,
            wrap=True,
        )

        self.canvas.draw_idle()