from dataclasses import dataclass


@dataclass
class RequirementProfile:
    """Preferred driver parameter ranges for a specific application."""

    name: str

    qts_min: float | None = None
    qts_max: float | None = None

    qes_min: float | None = None
    qes_max: float | None = None

    fs_max: float | None = None
    vas_max: float | None = None

    sd_min: float | None = None
    xmax_min: float | None = None
    bl_min: float | None = None

    sd_max: float | None = None
    xmax_max: float | None = None
    bl_max: float | None = None


PROFILES = {
    "hifi_woofer": RequirementProfile(
        name="Hi-Fi Woofer",
        qts_min=0.25,
        qts_max=0.50,
        qes_min=0.25,
        qes_max=0.60,
        fs_max=50.0,
        vas_max=80.0,
        sd_min=120.0,
        xmax_min=5.0,
        bl_min=6.0,
    ),
    "microspeaker": RequirementProfile(
    name="Microspeaker",
    qts_min=0.60,
    qts_max=1.50,
    qes_min=0.60,
    qes_max=2.00,
    fs_max=1200.0,
    vas_max=0.05,
    sd_min=1.0,
    sd_max=5.0,
    xmax_min=0.2,
    xmax_max=1.5,
    bl_min=0.05,
    bl_max=1.0,
    ),
    "subwoofer": RequirementProfile(
        name="Subwoofer",
        qts_min=0.25,
        qts_max=0.70,
        qes_min=0.25,
        qes_max=0.80,
        fs_max=35.0,
        vas_max=300.0,
        sd_min=300.0,
        xmax_min=10.0,
        bl_min=10.0,
    ),
}