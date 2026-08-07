"""Automotive Unit Extractor and Normalizer (RFC-AUTO-001).

Deterministic extraction, normalization, and association of engineering measurement units
found in OEM workshop manual tables across torque, pressure, clearance, fluid volume,
electrical, temperature, speed, angle, mass, and dimension metrics.
"""

from __future__ import annotations

import re

# Comprehensive compiled regex for automotive engineering units
_UNIT_PATTERN = re.compile(
    r"""(?xi)
    \b(?:
        # Torque
        N[·\.\s]?m|N-m|Nm|
        (?:ft|in)[-\.\s]?(?:lb|lbs)|
        kgf[-\.\s]?(?:m|cm)|kg[-\.\s]?(?:m|cm)|
        # Length / Clearance / Thickness
        mm|cm|m|μm|um|inch|inches|in|\"|
        # Pressure
        kPa|MPa|psi|bar|kgf/cm[²2]|mmHg|inHg|hPa|
        # Fluid Volume
        L|liter|liters|litres|qt|qts|quarts|gal|gallons|pt|pints|ml|mL|cc|cm[³3]|
        # Electrical
        V|mV|kV|A|mA|μA|uA|k?M?Ω|k?M?ohm|ohms|W|kW|Hz|kHz|
        # Rotational / Velocity
        rpm|RPM|r/min|km/h|mph|m/s|
        # Temperature
        °C|deg(?:\.|\s+)?C|°F|deg(?:\.|\s+)?F|K|
        # Mass
        g|kg|oz|lbs?|
        # Angle
        deg|degrees?|°|%
    )\b
    """,
)

# Parenthesized / Bracketed Unit Extraction
_PARENTHESIZED_UNIT_RE = re.compile(
    r"[\(\[\{]\s*("
    r"N[·\.\s]?m|N-m|Nm|"
    r"(?:ft|in)[-\.\s]?(?:lb|lbs)|"
    r"kgf[-\.\s]?(?:m|cm)|kg[-\.\s]?(?:m|cm)|"
    r"mm|cm|m|μm|um|inch|inches|in|"
    r"kPa|MPa|psi|bar|kgf/cm[²2]|mmHg|inHg|hPa|"
    r"L|liter|liters|litres|qt|qts|quarts|gal|gallons|pt|pints|ml|mL|cc|cm[³3]|"
    r"V|mV|kV|A|mA|μA|uA|k?M?Ω|k?M?ohm|ohms|W|kW|Hz|kHz|"
    r"rpm|RPM|r/min|km/h|mph|m/s|"
    r"°C|deg(?:\.|\s+)?C|°F|deg(?:\.|\s+)?F|K|"
    r"g|kg|oz|lbs?|"
    r"deg|degrees?|°|%"
    r")\s*[\)\]\}]",
    re.IGNORECASE,
)

# Canonical Unit Normalization Map
_CANONICAL_UNIT_MAP: dict[str, str] = {
    # Torque
    "nm": "N·m",
    "n.m": "N·m",
    "n m": "N·m",
    "n-m": "N·m",
    "n·m": "N·m",
    "ft-lb": "ft-lb",
    "ft.lb": "ft-lb",
    "ft-lbs": "ft-lb",
    "ft lb": "ft-lb",
    "ft lbs": "ft-lb",
    "in-lb": "in-lb",
    "in.lb": "in-lb",
    "in-lbs": "in-lb",
    "in lb": "in-lb",
    "kgf-m": "kgf-m",
    "kgf.m": "kgf-m",
    "kgf m": "kgf-m",
    "kg-m": "kgf-m",
    "kgf-cm": "kgf-cm",
    "kgf.cm": "kgf-cm",
    "kg-cm": "kgf-cm",
    # Length
    "mm": "mm",
    "cm": "cm",
    "m": "m",
    "μm": "μm",
    "um": "μm",
    "inch": "in",
    "inches": "in",
    '"': "in",
    # Pressure
    "kpa": "kPa",
    "mpa": "MPa",
    "psi": "psi",
    "bar": "bar",
    "kgf/cm2": "kgf/cm²",
    "kgf/cm²": "kgf/cm²",
    "mmhg": "mmHg",
    "inhg": "inHg",
    "hpa": "hPa",
    # Fluid Volume
    "l": "L",
    "liter": "L",
    "liters": "L",
    "litres": "L",
    "qt": "qt",
    "qts": "qt",
    "quarts": "qt",
    "gal": "gal",
    "gallons": "gal",
    "pt": "pt",
    "pints": "pt",
    "ml": "mL",
    "cc": "cc",
    "cm3": "cm³",
    "cm³": "cm³",
    # Electrical
    "v": "V",
    "mv": "mV",
    "kv": "kV",
    "a": "A",
    "ma": "mA",
    "μa": "μA",
    "ua": "μA",
    "ω": "Ω",
    "kω": "kΩ",
    "mω": "MΩ",
    "ohm": "Ω",
    "ohms": "Ω",
    "kohm": "kΩ",
    "mohm": "MΩ",
    "w": "W",
    "kw": "kW",
    "hz": "Hz",
    "khz": "kHz",
    # Velocity / Speed
    "rpm": "rpm",
    "r/min": "rpm",
    "km/h": "km/h",
    "mph": "mph",
    "m/s": "m/s",
    # Temperature
    "°c": "°C",
    "deg c": "°C",
    "deg. c": "°C",
    "°f": "°F",
    "deg f": "°F",
    "deg. f": "°F",
    "k": "K",
    # Mass
    "g": "g",
    "kg": "kg",
    "oz": "oz",
    "lb": "lb",
    "lbs": "lb",
    # Angle / Ratio
    "deg": "°",
    "degree": "°",
    "degrees": "°",
    "°": "°",
    "%": "%",
}


class AutomotiveUnitExtractor:
    """Deterministic extractor for automotive units across headers, cells, and unit rows."""

    @staticmethod
    def extract_unit_from_header(text: str) -> str | None:
        """Extract measurement unit from column header string (e.g. 'Torque (N·m)', 'Limit [mm]')."""
        if not text:
            return None

        # 1. Check parenthesized/bracketed units first
        paren_match = _PARENTHESIZED_UNIT_RE.search(text)
        if paren_match:
            raw_unit = paren_match.group(1).strip()
            return _CANONICAL_UNIT_MAP.get(raw_unit.lower(), raw_unit)

        # 2. Check general unit pattern
        unit_match = _UNIT_PATTERN.search(text)
        if unit_match:
            raw_unit = unit_match.group(0).strip()
            return _CANONICAL_UNIT_MAP.get(raw_unit.lower(), raw_unit)

        return None

    @staticmethod
    def extract_unit_from_value(text: str) -> tuple[str, str | None]:
        """Separate numeric value and unit from cell string (e.g. '15.5 N·m' -> ('15.5', 'N·m'))."""
        if not text:
            return "", None

        stripped = text.strip()
        match = _UNIT_PATTERN.search(stripped)
        if match:
            raw_unit = match.group(0).strip()
            canonical = _CANONICAL_UNIT_MAP.get(raw_unit.lower(), raw_unit)
            # Remove unit from value
            val_clean = (
                stripped[: match.start()] + stripped[match.end() :]
            ).strip()
            return val_clean, canonical

        return stripped, None

    @staticmethod
    def is_unit_row(cell_texts: list[str]) -> bool:
        """Determine if a table row exclusively contains measurement units."""
        if not cell_texts:
            return False

        non_empty = [c.strip() for c in cell_texts if c.strip()]
        if not non_empty:
            return False

        unit_count = sum(
            1
            for c in non_empty
            if _UNIT_PATTERN.fullmatch(c)
            or _PARENTHESIZED_UNIT_RE.fullmatch(c)
            or c.lower() in _CANONICAL_UNIT_MAP
        )

        return unit_count >= max(1, len(non_empty) // 2)

    @staticmethod
    def normalize_unit(raw_unit: str) -> str:
        """Normalize an automotive unit to standard canonical typography."""
        return _CANONICAL_UNIT_MAP.get(raw_unit.strip().lower(), raw_unit.strip())
