from dataclasses import dataclass


@dataclass
class Driver:
    """
    Represents a loudspeaker driver.
    """

    manufacturer: str
    model: str

    fs: float      # Resonance frequency (Hz)
    qts: float
    qes: float
    qms: float

    vas: float     # Litres

    re: float      # DC resistance (Ohms)
    le: float      # Voice coil inductance (mH)

    sd: float      # Effective piston area (cm²)

    xmax: float    # Linear excursion (mm)

    bl: float      # Force factor (N/A)

    mms: float     # Moving mass (g)

    cms: float     # Compliance (mm/N)

    def summary(self):
        print("=" * 40)
        print(f"{self.manufacturer} {self.model}")
        print("=" * 40)
        print(f"Fs   : {self.fs} Hz")
        print(f"Qts  : {self.qts}")
        print(f"Qes  : {self.qes}")
        print(f"Qms  : {self.qms}")
        print(f"Vas  : {self.vas} L")
        print(f"Re   : {self.re} Ω")
        print(f"Le   : {self.le} mH")
        print(f"Sd   : {self.sd} cm²")
        print(f"Xmax : {self.xmax} mm")
        print(f"BL   : {self.bl} N/A")
        print(f"Mms  : {self.mms} g")
        print(f"Cms  : {self.cms} mm/N")