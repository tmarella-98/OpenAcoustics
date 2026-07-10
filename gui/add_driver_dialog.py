from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QVBoxLayout,
)

from acoustics.driver import Driver


class AddDriverDialog(QDialog):
    """Dialog for manually adding a driver to the database."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Add Driver")
        self.resize(420, 600)

        self.manufacturer_input = QLineEdit()
        self.model_input = QLineEdit()

        self.fs_input = self._create_spinbox(0.01, 100_000.0, 2, " Hz")
        self.qts_input = self._create_spinbox(0.001, 100.0, 4)
        self.qes_input = self._create_spinbox(0.001, 100.0, 4)
        self.qms_input = self._create_spinbox(0.001, 1000.0, 4)

        self.vas_input = self._create_spinbox(0.000001, 100_000.0, 6, " L")

        self.re_input = self._create_spinbox(0.001, 1000.0, 3, " Ω")
        self.le_input = self._create_spinbox(0.0, 1000.0, 4, " mH")

        self.sd_input = self._create_spinbox(0.0001, 100_000.0, 4, " cm²")
        self.xmax_input = self._create_spinbox(0.0, 1000.0, 4, " mm")
        self.bl_input = self._create_spinbox(0.0, 10_000.0, 4, " N/A")
        self.mms_input = self._create_spinbox(0.0001, 100_000.0, 4, " g")
        self.cms_input = self._create_spinbox(0.000001, 100_000.0, 6, " mm/N")

        form_layout = QFormLayout()
        form_layout.addRow("Manufacturer", self.manufacturer_input)
        form_layout.addRow("Model", self.model_input)
        form_layout.addRow("Fs", self.fs_input)
        form_layout.addRow("Qts", self.qts_input)
        form_layout.addRow("Qes", self.qes_input)
        form_layout.addRow("Qms", self.qms_input)
        form_layout.addRow("Vas", self.vas_input)
        form_layout.addRow("Re", self.re_input)
        form_layout.addRow("Le", self.le_input)
        form_layout.addRow("Sd", self.sd_input)
        form_layout.addRow("Xmax", self.xmax_input)
        form_layout.addRow("BL", self.bl_input)
        form_layout.addRow("Mms", self.mms_input)
        form_layout.addRow("Cms", self.cms_input)

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(self.buttons)

        self.setLayout(layout)

    @staticmethod
    def _create_spinbox(
        minimum: float,
        maximum: float,
        decimals: int,
        suffix: str = "",
    ) -> QDoubleSpinBox:
        spinbox = QDoubleSpinBox()
        spinbox.setRange(minimum, maximum)
        spinbox.setDecimals(decimals)
        spinbox.setSuffix(suffix)
        spinbox.setKeyboardTracking(False)
        return spinbox

    def validate_and_accept(self) -> None:
        manufacturer = self.manufacturer_input.text().strip()
        model = self.model_input.text().strip()

        if not manufacturer:
            QMessageBox.warning(
                self,
                "Missing manufacturer",
                "Enter the driver manufacturer.",
            )
            return

        if not model:
            QMessageBox.warning(
                self,
                "Missing model",
                "Enter the driver model.",
            )
            return

        self.accept()

    def get_driver(self) -> Driver:
        """Create a Driver from the values entered by the user."""
        return Driver(
            manufacturer=self.manufacturer_input.text().strip(),
            model=self.model_input.text().strip(),
            fs=self.fs_input.value(),
            qts=self.qts_input.value(),
            qes=self.qes_input.value(),
            qms=self.qms_input.value(),
            vas=self.vas_input.value(),
            re=self.re_input.value(),
            le=self.le_input.value(),
            sd=self.sd_input.value(),
            xmax=self.xmax_input.value(),
            bl=self.bl_input.value(),
            mms=self.mms_input.value(),
            cms=self.cms_input.value(),
        )