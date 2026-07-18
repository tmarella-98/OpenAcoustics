import numpy as np

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QSlider,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from acoustics.bass_reflex import BassReflex
from acoustics.bass_reflex_port import BassReflexPortCalculator
from acoustics.driver_model import DriverModel
from acoustics.impedance import ImpedanceCalculator
from acoustics.sealed_box import SealedBox
from core.enclosures.bass_reflex import BassReflexEnclosure
from core.enclosures.sealed import SealedEnclosure
from core.project import Project
from gui.mpl_canvas import MplCanvas


class SimulationWorkspace(QWidget):
    """Workspace containing enclosure controls, results and plots."""

    def __init__(
        self,
        project: Project,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.project = project
        self._updating_controls = False

        self.response_frequencies_hz = np.logspace(
            np.log10(10.0),
            np.log10(1000.0),
            1200,
        )

        self.impedance_frequencies_hz = np.logspace(
            np.log10(5.0),
            np.log10(20_000.0),
            2000,
        )

        self.create_widgets()
        self.create_layout()
        self.connect_signals()
        self.set_project(project)

    def create_widgets(self) -> None:
        """Create all workspace controls, labels and plot tabs."""
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

        # The slider uses tenths of a litre:
        # 1 means 0.1 L and 10,000 means 1000 L.
        self.volume_slider = QSlider(
            Qt.Orientation.Horizontal
        )
        self.volume_slider.setRange(1, 10_000)
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
        self.port_length_label = QLabel("Port length: N/A")

        self.re_label = QLabel("Re: N/A")
        self.fs_label = QLabel("Fs: N/A")
        self.peak_impedance_label = QLabel(
            "Peak impedance: N/A"
        )

        self.status_label = QLabel(
            "Select a driver to begin."
        )
        self.status_label.setWordWrap(True)

        self.plot_tabs = QTabWidget()

        self.response_canvas = MplCanvas(
            width=8.0,
            height=5.0,
            dpi=100,
        )

        self.impedance_canvas = MplCanvas(
            width=8.0,
            height=5.0,
            dpi=100,
        )

        self.excursion_placeholder = QLabel(
            "Cone excursion coming soon"
        )
        self.excursion_placeholder.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.port_velocity_placeholder = QLabel(
            "Port velocity coming soon"
        )
        self.port_velocity_placeholder.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.plot_tabs.addTab(
            self.response_canvas,
            "Frequency Response",
        )

        self.plot_tabs.addTab(
            self.impedance_canvas,
            "Impedance",
        )

        self.plot_tabs.addTab(
            self.excursion_placeholder,
            "Excursion",
        )

        self.plot_tabs.addTab(
            self.port_velocity_placeholder,
            "Port Velocity",
        )

    def create_layout(self) -> None:
        """Create and assign the workspace layout."""
        self.simulation_group = QGroupBox(
            "Simulation"
        )

        self.simulation_form = QFormLayout()

        self.simulation_form.addRow(
            "Type",
            self.simulation_type_selector,
        )

        self.simulation_form.addRow(
            "Box volume",
            self.volume_spinbox,
        )

        self.simulation_form.addRow(
            "",
            self.volume_slider,
        )

        self.simulation_form.addRow(
            "Tuning frequency",
            self.tuning_spinbox,
        )

        self.simulation_form.addRow(
            "Port diameter",
            self.port_diameter_spinbox,
        )

        self.simulation_group.setLayout(
            self.simulation_form
        )

        results_group = QGroupBox(
            "Results"
        )

        results_form = QFormLayout()

        results_form.addRow(self.driver_label)
        results_form.addRow(self.fc_label)
        results_form.addRow(self.qtc_label)
        results_form.addRow(self.f3_label)
        results_form.addRow(self.fb_label)
        results_form.addRow(self.port_length_label)
        results_form.addRow(self.fs_label)
        results_form.addRow(self.re_label)
        results_form.addRow(
            self.peak_impedance_label
        )
        results_form.addRow(self.status_label)

        results_group.setLayout(
            results_form
        )

        layout = QVBoxLayout()
        layout.addWidget(self.simulation_group)
        layout.addWidget(results_group)
        layout.addWidget(
            self.plot_tabs,
            stretch=1,
        )

        self.setLayout(layout)

    def connect_signals(self) -> None:
        """Connect control changes to simulation updates."""
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
        """Load enclosure controls from the current project."""
        self._updating_controls = True

        try:
            enclosure = self.project.enclosure

            if isinstance(
                enclosure,
                SealedEnclosure,
            ):
                sealed_index = (
                    self.simulation_type_selector.findData(
                        "sealed"
                    )
                )

                self.simulation_type_selector.setCurrentIndex(
                    sealed_index
                )

                self.set_volume_value(
                    enclosure.volume_l
                )

            elif isinstance(
                enclosure,
                BassReflexEnclosure,
            ):
                bass_reflex_index = (
                    self.simulation_type_selector.findData(
                        "bass_reflex"
                    )
                )

                self.simulation_type_selector.setCurrentIndex(
                    bass_reflex_index
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
                sealed_index = (
                    self.simulation_type_selector.findData(
                        "sealed"
                    )
                )

                self.simulation_type_selector.setCurrentIndex(
                    sealed_index
                )

                self.set_volume_value(10.0)

        finally:
            self._updating_controls = False

        self.update_control_visibility()

    def update_control_visibility(self) -> None:
        """Show only controls relevant to the enclosure type."""
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

        tuning_label = (
            self.simulation_form.labelForField(
                self.tuning_spinbox
            )
        )

        port_label = (
            self.simulation_form.labelForField(
                self.port_diameter_spinbox
            )
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
        """Handle an enclosure-type selection change."""
        if self._updating_controls:
            return

        self.update_control_visibility()
        self.update_simulation()

    def on_volume_spinbox_changed(
        self,
        volume_l: float,
    ) -> None:
        """Synchronize the volume slider with the spinbox."""
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
        """Synchronize the volume spinbox with the slider."""
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
        """Set both volume controls."""
        self.volume_spinbox.setValue(
            volume_l
        )

        self.volume_slider.setValue(
            int(round(volume_l * 10.0))
        )

    def update_simulation(
        self,
        *_args,
    ) -> None:
        """Recalculate all available analyses and redraw plots."""
        if self._updating_controls:
            return

        driver = self.project.driver

        if driver is None:
            self.show_no_driver_state()
            self.update_impedance_plot()
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

        # This is currently free-air impedance, so it depends on the
        # selected driver but not yet on the selected enclosure.
        self.update_impedance_plot()

    def run_sealed_simulation(self) -> None:
        """Run and display the sealed-box response."""
        driver = self.project.driver

        if driver is None:
            return

        volume_l = self.volume_spinbox.value()

        enclosure = SealedEnclosure(
            volume_l=volume_l
        )

        self.project.set_enclosure(
            enclosure
        )

        simulation = SealedBox(
            driver=driver,
            volume_l=volume_l,
        )

        simulation.calculate()

        magnitude_db = (
            simulation.calculate_transfer_function(
                self.response_frequencies_hz
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

        self.port_length_label.setText(
            "Port length: N/A"
        )

        self.status_label.setText(
            "Sealed-box simulation calculated successfully."
        )

        axes = self.response_canvas.axes
        axes.clear()

        axes.semilogx(
            self.response_frequencies_hz,
            magnitude_db,
            label=(
                f"Sealed — {volume_l:.1f} L"
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
            label=f"Fc = {simulation.fc_hz:.1f} Hz",
        )

        axes.axvline(
            simulation.f3_hz,
            linestyle="--",
            linewidth=1,
            label=f"F3 = {simulation.f3_hz:.1f} Hz",
        )

        self.finish_response_plot(
            title=(
                f"{driver.manufacturer} "
                f"{driver.model}\n"
                "Sealed-box transfer function"
            ),
            y_min=-30.0,
            y_max=6.0,
        )

    def run_bass_reflex_simulation(self) -> None:
        """Run and display the bass-reflex response."""
        driver = self.project.driver

        if driver is None:
            return

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
            driver=driver,
            enclosure=enclosure,
        )

        simulation.calculate()

        magnitude_db = (
            simulation.calculate_transfer_function(
                self.response_frequencies_hz
            )
        )

        port_calculator = (
            BassReflexPortCalculator()
        )

        port_result = (
            port_calculator.calculate_required_length(
                enclosure
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

        self.port_length_label.setText(
            "Port length: "
            f"{port_result.physical_length_mm:.1f} mm"
        )

        self.status_label.setText(
            "Bass-reflex simulation calculated successfully."
        )

        axes = self.response_canvas.axes
        axes.clear()

        axes.semilogx(
            self.response_frequencies_hz,
            magnitude_db,
            label=(
                f"Bass reflex — {volume_l:.1f} L, "
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
            label=f"F3 = {simulation.f3_hz:.1f} Hz",
        )

        self.finish_response_plot(
            title=(
                f"{driver.manufacturer} "
                f"{driver.model}\n"
                "Bass-reflex transfer function"
            ),
            y_min=-40.0,
            y_max=10.0,
        )

    def update_impedance_plot(self) -> None:
        """Calculate and plot free-air electrical impedance."""
        driver = self.project.driver

        axes = self.impedance_canvas.axes
        axes.clear()

        if driver is None:
            self.re_label.setText(
                "Re: N/A"
            )

            self.fs_label.setText(
                "Fs: N/A"
            )

            self.peak_impedance_label.setText(
                "Peak impedance: N/A"
            )

            axes.set_title(
                "No driver selected"
            )

            axes.set_xlabel(
                "Frequency (Hz)"
            )

            axes.set_ylabel(
                "Impedance magnitude (Ω)"
            )

            axes.set_xscale("log")
            axes.grid(
                True,
                which="both",
            )

            self.impedance_canvas.draw_idle()
            return

        try:
            model = DriverModel(driver)

            calculator = ImpedanceCalculator(
                model
            )

            result = calculator.calculate(
                self.impedance_frequencies_hz
            )

        except Exception as error:
            self.re_label.setText(
                "Re: N/A"
            )

            self.fs_label.setText(
                "Fs: N/A"
            )

            self.peak_impedance_label.setText(
                "Peak impedance: N/A"
            )

            axes.set_title(
                "Impedance unavailable"
            )

            axes.text(
                0.5,
                0.5,
                str(error),
                horizontalalignment="center",
                verticalalignment="center",
                transform=axes.transAxes,
                wrap=True,
            )

            self.impedance_canvas.draw_idle()
            return

        peak_index = int(
            np.argmax(result.magnitude_ohm)
        )

        peak_impedance_ohm = float(
            result.magnitude_ohm[peak_index]
        )

        peak_frequency_hz = float(
            result.frequency_hz[peak_index]
        )

        self.re_label.setText(
            f"Re: {model.re:.2f} Ω"
        )

        self.fs_label.setText(
            f"Fs: {model.fs:.2f} Hz"
        )

        self.peak_impedance_label.setText(
            "Peak impedance: "
            f"{peak_impedance_ohm:.2f} Ω "
            f"at {peak_frequency_hz:.1f} Hz"
        )

        axes.semilogx(
            result.frequency_hz,
            result.magnitude_ohm,
            label="Free-air impedance",
        )

        axes.axvline(
            model.fs,
            linestyle="--",
            linewidth=1,
            label=f"Fs = {model.fs:.1f} Hz",
        )

        axes.set_xlabel(
            "Frequency (Hz)"
        )

        axes.set_ylabel(
            "Impedance magnitude (Ω)"
        )

        axes.set_title(
            f"{driver.manufacturer} "
            f"{driver.model}\n"
            "Free-air electrical impedance"
        )

        axes.set_xlim(
            self.impedance_frequencies_hz[0],
            self.impedance_frequencies_hz[-1],
        )

        axes.grid(
            True,
            which="both",
        )

        axes.legend()

        self.impedance_canvas.figure.tight_layout()
        self.impedance_canvas.draw_idle()

    def finish_response_plot(
        self,
        title: str,
        y_min: float,
        y_max: float,
    ) -> None:
        """Apply common formatting to the response plot."""
        axes = self.response_canvas.axes

        axes.set_xlabel(
            "Frequency (Hz)"
        )

        axes.set_ylabel(
            "Transfer function magnitude (dB)"
        )

        axes.set_title(title)

        axes.set_xlim(
            self.response_frequencies_hz[0],
            self.response_frequencies_hz[-1],
        )

        axes.set_ylim(
            y_min,
            y_max,
        )

        axes.grid(
            True,
            which="both",
        )

        axes.legend()

        self.response_canvas.figure.tight_layout()
        self.response_canvas.draw_idle()

    def show_no_driver_state(self) -> None:
        """Display empty plots and labels when no driver is selected."""
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

        self.port_length_label.setText(
            "Port length: N/A"
        )

        self.status_label.setText(
            "Select a driver in the Driver Explorer."
        )

        axes = self.response_canvas.axes
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

        axes.set_xscale("log")

        axes.grid(
            True,
            which="both",
        )

        self.response_canvas.draw_idle()

    def show_simulation_error(
        self,
        message: str,
    ) -> None:
        """Display a response-simulation error without crashing."""
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

        self.port_length_label.setText(
            "Port length: N/A"
        )

        self.status_label.setText(
            f"Simulation unavailable: {message}"
        )

        axes = self.response_canvas.axes
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

        self.response_canvas.draw_idle()