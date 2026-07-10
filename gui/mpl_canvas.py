from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):
    """Reusable Matplotlib canvas for OpenAcoustics plots."""

    def __init__(
        self,
        width: float = 8.0,
        height: float = 5.0,
        dpi: int = 100,
    ) -> None:
        self.figure = Figure(
            figsize=(width, height),
            dpi=dpi,
        )

        self.axes = self.figure.add_subplot(111)

        super().__init__(self.figure)