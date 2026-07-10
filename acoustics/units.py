def litres_to_cubic_metres(value_l: float) -> float:
    """Convert litres to cubic metres."""
    return value_l / 1000.0


def cubic_metres_to_litres(value_m3: float) -> float:
    """Convert cubic metres to litres."""
    return value_m3 * 1000.0


def square_centimetres_to_square_metres(value_cm2: float) -> float:
    """Convert square centimetres to square metres."""
    return value_cm2 / 10_000.0


def millimetres_to_metres(value_mm: float) -> float:
    """Convert millimetres to metres."""
    return value_mm / 1000.0


def grams_to_kilograms(value_g: float) -> float:
    """Convert grams to kilograms."""
    return value_g / 1000.0


def millihenries_to_henries(value_mh: float) -> float:
    """Convert millihenries to henries."""
    return value_mh / 1000.0