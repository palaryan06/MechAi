"""Configuration parameters for the Automotive Diagram Intelligence Engine."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class DiagramEngineConfig:
    """Immutable calibration thresholds and patterns for diagram detection."""

    # -----------------------------------------------------------------------
    # Spatial Thresholds (in points)
    # -----------------------------------------------------------------------
    proximity_threshold_pt: float = 40.0
    """Maximum distance to consider a label 'adjacent' to a callout without a leader line."""

    alignment_tolerance_pt: float = 10.0
    """Tolerance for vertical/horizontal alignment checks."""

    # -----------------------------------------------------------------------
    # Callout Patterns
    # -----------------------------------------------------------------------
    callout_patterns: tuple[re.Pattern, ...] = field(
        default_factory=lambda: (
            # Numeric callouts: 1, 2, 3...
            re.compile(r"^\d{1,3}$"),
            # Alphabetic callouts: A, B, C...
            re.compile(r"^[A-Z]$"),
            # Bracketed callouts: [1], [A]
            re.compile(r"^\[(?:[A-Z]|\d{1,3})\]$"),
            # Parenthesized callouts: (1), (A)
            re.compile(r"^\((?:[A-Z]|\d{1,3})\)$"),
        )
    )

    # -----------------------------------------------------------------------
    # Figure Patterns
    # -----------------------------------------------------------------------
    figure_prefix_patterns: tuple[re.Pattern, ...] = field(
        default_factory=lambda: (
            re.compile(r"^(?:Fig\.?|Figure|Illustration|Diagram)\s*([\dA-Z\-]+)", re.IGNORECASE),
        )
    )

    # -----------------------------------------------------------------------
    # Component Patterns
    # -----------------------------------------------------------------------
    connector_keywords: tuple[str, ...] = (
        "connector",
        "terminal",
        "pin",
        "harness",
        "plug",
        "socket",
        "wire",
    )

    circuit_keywords: tuple[str, ...] = (
        "circuit",
        "relay",
        "fuse",
        "ground",
        "power",
        "switch",
        "sensor",
    )
