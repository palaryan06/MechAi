"""Configuration parameters for Automotive Safety Intelligence Engine."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from mechai.contracts.safety import HazardCategory, SafetySeverity


@dataclass(frozen=True)
class SafetyEngineConfig:
    """Immutable configuration for safety extraction and classification."""

    # -----------------------------------------------------------------------
    # Severity Patterns
    # -----------------------------------------------------------------------
    severity_map: dict[str, SafetySeverity] = field(
        default_factory=lambda: {
            "DANGER": SafetySeverity.DANGER,
            "WARNING": SafetySeverity.WARNING,
            "CAUTION": SafetySeverity.CAUTION,
            "NOTICE": SafetySeverity.NOTICE,
            "NOTE": SafetySeverity.NOTE,
            "IMPORTANT": SafetySeverity.IMPORTANT,
        }
    )

    # -----------------------------------------------------------------------
    # Hazard Keyword Mappings
    # -----------------------------------------------------------------------
    hazard_keywords: dict[str, HazardCategory] = field(
        default_factory=lambda: {
            "hot": HazardCategory.HOT_SURFACE,
            "burn": HazardCategory.HOT_SURFACE,
            "fire": HazardCategory.FIRE,
            "flame": HazardCategory.FIRE,
            "explosion": HazardCategory.EXPLOSION,
            "explosive": HazardCategory.EXPLOSION,
            "electrical": HazardCategory.ELECTRICAL,
            "shock": HazardCategory.ELECTRICAL,
            "high voltage": HazardCategory.HIGH_VOLTAGE,
            "pressure": HazardCategory.PRESSURE,
            "pressurized": HazardCategory.PRESSURE,
            "chemical": HazardCategory.CHEMICAL,
            "toxic": HazardCategory.TOXIC_SUBSTANCE,
            "poison": HazardCategory.TOXIC_SUBSTANCE,
            "rotating": HazardCategory.ROTATING_COMPONENT,
            "moving": HazardCategory.MOVING_COMPONENT,
            "crush": HazardCategory.CRUSHING,
            "pinch": HazardCategory.CRUSHING,
            "vehicle movement": HazardCategory.VEHICLE_MOVEMENT,
            "jack": HazardCategory.JACKING_SUPPORT,
            "hoist": HazardCategory.JACKING_SUPPORT,
            "fuel": HazardCategory.FUEL,
            "coolant": HazardCategory.COOLANT,
            "oil": HazardCategory.OIL,
            "battery": HazardCategory.BATTERY,
            "airbag": HazardCategory.AIRBAG,
            "brake fluid": HazardCategory.BRAKE_SYSTEM,
        }
    )

    # -----------------------------------------------------------------------
    # Contextual Markers (Regexes for extracting clauses)
    # -----------------------------------------------------------------------
    condition_patterns: tuple[re.Pattern, ...] = field(
        default_factory=lambda: (
            re.compile(r"(?i)\b(?:when|if|after|before|during|while|in case of)\b[^,.]+", re.IGNORECASE),
        )
    )

    consequence_patterns: tuple[re.Pattern, ...] = field(
        default_factory=lambda: (
            re.compile(r"(?i)\b(?:may result in|can cause|will lead to|could cause|result in|cause)\b[^,.]+", re.IGNORECASE),
        )
    )

    action_patterns: tuple[re.Pattern, ...] = field(
        default_factory=lambda: (
            re.compile(r"(?i)\b(?:always|never|do not|must|ensure|make sure|allow|keep|avoid)\b[^,.]+", re.IGNORECASE),
        )
    )

    ppe_keywords: tuple[str, ...] = (
        "safety glasses",
        "goggles",
        "gloves",
        "mask",
        "respirator",
        "face shield",
        "protective clothing",
    )

    # -----------------------------------------------------------------------
    # Proximity Thresholds
    # -----------------------------------------------------------------------
    procedure_binding_distance_pt: float = 60.0
