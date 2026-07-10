import numpy as np

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from acoustics.driver import Driver
from acoustics.sealed_box import SealedBox
from gui.mpl_canvas import MplCanvas


class MainWindow(QMainWindow):
    """Main OpenAcoustics application window."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("OpenAcoustics")
        self.resize(1200, 800)

        self.driver = Driver.load(
            "examples/SB17NBAC35-8.json"
        )

        self.frequencies_hz = np.logspace(
            np.log10(10.0),
            np.log10(1000.0),
            1000,
        )

        self.driver_label = QLabel(
            f"Driver: "
            f"{self.driver.manufacturer} "
            f"{self.driver.model}"
        )

        self.volume_label = QLabel(
            "Box volume: 10.0 L"
        )

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

        layout = QVBoxLayout()
        layout.addWidget(self.driver_label)
        layout.addWidget(self.volume_label)
        layout.addWidget(self.volume_slider)
        layout.addWidget(self.fc_label)
        layout.addWidget(self.qtc_label)
        layout.addWidget(self.f3_label)
        layout.addWidget(self.canvas)

        central_widget = QWidget()
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

        self.volume_slider.valueChanged.connect(
            self.update_simulation
        )

        self.update_simulation()

    def update_simulation(self) -> None:
        volume_l = self.volume_slider.value() / 10.0

        simulation = SealedBox(
            driver=self.driver,
            volume_l=volume_l,
        )
        simulation.calculate()

        magnitude_db = (
            simulation.calculate_transfer_function(
                self.frequencies_hz
            )
        )

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
            label="Transfer function",
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
            f"Sealed box — {volume_l:.1f} L"
        )

        axes.set_xlim(10.0, 1000.0)
        axes.set_ylim(-30.0, 6.0)
        axes.grid(True, which="both")
        axes.legend()

        self.canvas.figure.tight_layout()
        self.canvas.draw_idle()