"""Configuration for Specification and Torque Extraction Engine."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class UnitNormalizationRule:
    """Rule for normalizing a specific unit string to a canonical unit."""

    canonical_unit: str
    conversion_factor: float
    regex_pattern: re.Pattern[str]


@dataclass(frozen=True)
class SpecificationConfig:
    """Configuration and patterns for specification extraction."""

    # Patterns for extracting values with units (e.g. "45 N.m", "4.5 kgf-m", "0.13-0.17 mm")
    # Captures:
    # 1. value string (can include ranges or tolerances, e.g. "45", "45-50", "45 - 50", "0.13", "45 +/- 2")
    # 2. unit string (e.g. "N.m", "kgf-m", "mm")
    value_with_unit_pattern: re.Pattern[str] = field(
        default_factory=lambda: re.compile(
            r"((?:[-+]?\d*\.?\d+(?:\s*(?:-|~|to|\+/-|±)\s*[-+]?\d*\.?\d+)?))"  # Value(s)
            r"(?:\s+"
            r"([a-zA-Z·](?:[a-zA-Z·\-\.\/]*[a-zA-Z·])?))?"  # Optional Unit, no trailing dots
        )
    )

    # Patterns for single numeric values without units
    numeric_pattern: re.Pattern[str] = field(
        default_factory=lambda: re.compile(r"^[-+]?\d*\.?\d+$")
    )

    # Patterns for range extraction from strings like "45-50" or "0.13 ~ 0.17"
    range_pattern: re.Pattern[str] = field(
        default_factory=lambda: re.compile(r"([-+]?\d*\.?\d+)\s*(?:-|~|to)\s*([-+]?\d*\.?\d+)")
    )

    # Patterns for tolerance like "45 +/- 2" or "45 ± 2"
    tolerance_pattern: re.Pattern[str] = field(
        default_factory=lambda: re.compile(r"([-+]?\d*\.?\d+)\s*(?:\+/-|±)\s*([-+]?\d*\.?\d+)")
    )

    # Tightening angle pattern like "+ 90°" or "and 90 degrees"
    angle_pattern: re.Pattern[str] = field(
        default_factory=lambda: re.compile(r"(?:\+|,? and)?\s*(\d+)\s*(?:°|degrees|deg\.?)", re.IGNORECASE)
    )

    # Mapping of raw unit regexes to their canonical counterparts and conversion multipliers
    # Base canonical units: N.m, mm, L, kPa, C, V, A, ohm
    unit_rules: tuple[UnitNormalizationRule, ...] = field(
        default_factory=lambda: (
            # Torque
            UnitNormalizationRule("N.m", 1.0, re.compile(r"^(?:N\.m|N-m|Nm|N·m)$", re.IGNORECASE)),
            UnitNormalizationRule("N.m", 9.80665, re.compile(r"^(?:kgf\.m|kgf-m|kg-m|kgm)$", re.IGNORECASE)),
            UnitNormalizationRule("N.m", 0.0980665, re.compile(r"^(?:kgf\.cm|kgf-cm|kg-cm|kgcm)$", re.IGNORECASE)),
            UnitNormalizationRule("N.m", 1.355818, re.compile(r"^(?:ft-lb|ft\.lb|lb-ft|lb\.ft)$", re.IGNORECASE)),
            UnitNormalizationRule("N.m", 0.1129848, re.compile(r"^(?:in-lb|in\.lb|lb-in|lb\.in)$", re.IGNORECASE)),
            # Length
            UnitNormalizationRule("mm", 1.0, re.compile(r"^mm$", re.IGNORECASE)),
            UnitNormalizationRule("mm", 10.0, re.compile(r"^cm$", re.IGNORECASE)),
            UnitNormalizationRule("mm", 1000.0, re.compile(r"^m$", re.IGNORECASE)),
            UnitNormalizationRule("mm", 25.4, re.compile(r"^in(?:ch|ches)?$", re.IGNORECASE)),
            # Volume
            UnitNormalizationRule("L", 1.0, re.compile(r"^L(?:iters?)?$", re.IGNORECASE)),
            UnitNormalizationRule("L", 0.001, re.compile(r"^(?:mL|cc)$", re.IGNORECASE)),
            # Pressure
            UnitNormalizationRule("kPa", 1.0, re.compile(r"^kPa$", re.IGNORECASE)),
            UnitNormalizationRule("kPa", 1000.0, re.compile(r"^MPa$", re.IGNORECASE)),
            UnitNormalizationRule("kPa", 100.0, re.compile(r"^bar$", re.IGNORECASE)),
            UnitNormalizationRule("kPa", 6.89476, re.compile(r"^psi$", re.IGNORECASE)),
            UnitNormalizationRule("kPa", 98.0665, re.compile(r"^(?:kgf/cm2|kg/cm2)$", re.IGNORECASE)),
            # Temperature
            UnitNormalizationRule("C", 1.0, re.compile(r"^(?:°C|C)$", re.IGNORECASE)),
            # Electrical
            UnitNormalizationRule("V", 1.0, re.compile(r"^V$", re.IGNORECASE)),
            UnitNormalizationRule("V", 0.001, re.compile(r"^mV$", re.IGNORECASE)),
            UnitNormalizationRule("A", 1.0, re.compile(r"^A$", re.IGNORECASE)),
            UnitNormalizationRule("A", 0.001, re.compile(r"^mA$", re.IGNORECASE)),
            UnitNormalizationRule("ohm", 1.0, re.compile(r"^(?:ohm|ohms|Ω)$", re.IGNORECASE)),
            UnitNormalizationRule("ohm", 1000.0, re.compile(r"^(?:kohm|kohms|kΩ)$", re.IGNORECASE)),
            UnitNormalizationRule("ohm", 1000000.0, re.compile(r"^(?:Mohm|Mohms|MΩ)$", re.IGNORECASE)),
        )
    )

    # Keywords that indicate conditional applicability
    condition_keywords: tuple[str, ...] = field(
        default_factory=lambda: (
            "when cold",
            "when hot",
            "cold engine",
            "hot engine",
            "after installation",
            "before installation",
            "with a/c",
            "without a/c",
            "engine running",
            "engine stopped",
            "transmission in neutral",
            "at idle",
            "after tightening",
            "before adjustment",
        )
    )

    # Keywords for fastener condition
    lubrication_keywords: tuple[str, ...] = field(
        default_factory=lambda: (
            "apply engine oil",
            "apply oil",
            "lubricate",
            "with oil",
        )
    )
    threadlocker_keywords: tuple[str, ...] = field(
        default_factory=lambda: (
            "apply thread lock",
            "thread lock",
            "threadlocker",
            "loctite",
        )
    )

    # Regex for stripping footnotes/references from tables (e.g. "*1", "*2")
    footnote_strip_pattern: re.Pattern[str] = field(
        default_factory=lambda: re.compile(r"\*(?:\d+|[a-z])\s*$")
    )
