import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider

from acoustics.driver import Driver
from acoustics.sealed_box import SealedBox


def plot_transfer_function(
    simulation: SealedBox,
    minimum_frequency_hz: float = 10.0,
    maximum_frequency_hz: float = 1000.0,
    points: int = 1000,
) -> None:
    """Plot a sealed-box transfer-function magnitude."""

    simulation._require_calculated()

    frequencies_hz = np.logspace(
        np.log10(minimum_frequency_hz),
        np.log10(maximum_frequency_hz),
        points,
    )

    magnitude_db = simulation.calculate_transfer_function(
        frequencies_hz
    )

    plt.figure(figsize=(9, 5))

    plt.semilogx(
        frequencies_hz,
        magnitude_db,
        label="Transfer function",
    )

    plt.axhline(-3.0, linestyle="--", linewidth=1)
    plt.axhline(0.0, linestyle=":", linewidth=1)

    plt.axvline(
        simulation.fc_hz,
        linestyle=":",
        linewidth=1,
        label=f"Fc = {simulation.fc_hz:.1f} Hz",
    )

    plt.axvline(
        simulation.f3_hz,
        linestyle="--",
        linewidth=1,
        label=f"F3 = {simulation.f3_hz:.1f} Hz",
    )

    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Transfer function magnitude (dB)")

    plt.title(
        f"{simulation.driver.manufacturer} "
        f"{simulation.driver.model}\n"
        f"Sealed box: {simulation.volume_l:.1f} L, "
        f"Qtc: {simulation.qtc:.3f}"
    )

    plt.xlim(
        minimum_frequency_hz,
        maximum_frequency_hz,
    )

    plt.ylim(-30.0, 6.0)
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()
    plt.show()


def plot_volume_slider(
    driver: Driver,
    initial_volume_l: float = 10.0,
    minimum_volume_l: float = 2.0,
    maximum_volume_l: float = 50.0,
    volume_step_l: float = 0.1,
    minimum_frequency_hz: float = 10.0,
    maximum_frequency_hz: float = 1000.0,
    points: int = 1000,
) -> None:
    """Interactively vary sealed-box volume using a slider."""

    if minimum_volume_l <= 0:
        raise ValueError(
            "Minimum enclosure volume must be greater than zero."
        )

    if maximum_volume_l <= minimum_volume_l:
        raise ValueError(
            "Maximum enclosure volume must exceed minimum volume."
        )

    if not minimum_volume_l <= initial_volume_l <= maximum_volume_l:
        raise ValueError(
            "Initial volume must be inside the slider range."
        )

    frequencies_hz = np.logspace(
        np.log10(minimum_frequency_hz),
        np.log10(maximum_frequency_hz),
        points,
    )

    simulation = SealedBox(
        driver=driver,
        volume_l=initial_volume_l,
    )
    simulation.calculate()

    magnitude_db = simulation.calculate_transfer_function(
        frequencies_hz
    )

    figure, axis = plt.subplots(figsize=(10, 6))
    figure.subplots_adjust(bottom=0.22)

    response_line, = axis.semilogx(
        frequencies_hz,
        magnitude_db,
        label="Transfer function",
    )

    axis.axhline(-3.0, linestyle="--", linewidth=1)
    axis.axhline(0.0, linestyle=":", linewidth=1)

    fc_line = axis.axvline(
        simulation.fc_hz,
        linestyle=":",
        linewidth=1,
        label=f"Fc = {simulation.fc_hz:.1f} Hz",
    )

    f3_line = axis.axvline(
        simulation.f3_hz,
        linestyle="--",
        linewidth=1,
        label=f"F3 = {simulation.f3_hz:.1f} Hz",
    )

    title = axis.set_title(
        f"{driver.manufacturer} {driver.model}\n"
        f"Vb = {initial_volume_l:.1f} L, "
        f"Qtc = {simulation.qtc:.3f}, "
        f"Fc = {simulation.fc_hz:.1f} Hz, "
        f"F3 = {simulation.f3_hz:.1f} Hz"
    )

    axis.set_xlabel("Frequency (Hz)")
    axis.set_ylabel("Transfer function magnitude (dB)")
    axis.set_xlim(
        minimum_frequency_hz,
        maximum_frequency_hz,
    )
    axis.set_ylim(-30.0, 6.0)
    axis.grid(True, which="both")
    axis.legend()

    slider_axis = figure.add_axes(
        [0.15, 0.08, 0.70, 0.04]
    )

    volume_slider = Slider(
        ax=slider_axis,
        label="Box volume (L)",
        valmin=minimum_volume_l,
        valmax=maximum_volume_l,
        valinit=initial_volume_l,
        valstep=volume_step_l,
    )

    def update_plot(volume_l: float) -> None:
        updated_simulation = SealedBox(
            driver=driver,
            volume_l=volume_l,
        )
        updated_simulation.calculate()

        updated_magnitude_db = (
            updated_simulation.calculate_transfer_function(
                frequencies_hz
            )
        )

        response_line.set_ydata(updated_magnitude_db)

        fc_line.set_xdata(
            [
                updated_simulation.fc_hz,
                updated_simulation.fc_hz,
            ]
        )

        fc_line.set_label(
            f"Fc = {updated_simulation.fc_hz:.1f} Hz"
        )

        f3_line.set_xdata(
            [
                updated_simulation.f3_hz,
                updated_simulation.f3_hz,
            ]
        )

        f3_line.set_label(
            f"F3 = {updated_simulation.f3_hz:.1f} Hz"
        )

        title.set_text(
            f"{driver.manufacturer} {driver.model}\n"
            f"Vb = {volume_l:.1f} L, "
            f"Qtc = {updated_simulation.qtc:.3f}, "
            f"Fc = {updated_simulation.fc_hz:.1f} Hz, "
            f"F3 = {updated_simulation.f3_hz:.1f} Hz"
        )

        axis.legend()
        figure.canvas.draw_idle()

    volume_slider.on_changed(update_plot)

    figure._volume_slider = volume_slider

    plt.show()