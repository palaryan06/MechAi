"""Automotive Table Classifier (RFC-AUTO-001).

Deterministic typographical and semantic classification of automotive tables into
10 distinct technical categories based on title, headers, units, and structural token distributions.
"""

from __future__ import annotations

import re
from typing import Sequence

from mechai.contracts.tables import AutomotiveTableType

# Regex patterns for automotive table domains
_TORQUE_RE = re.compile(
    r"\b(?:torque|tighten|tightening|fastener|bolt|nut|n[·\.\s]?m|ft[-\s]?lb|kgf[-\s]?m|in[-\s]?lb)\b",
    re.IGNORECASE,
)
_SERVICE_INTERVAL_RE = re.compile(
    r"\b(?:service\s+interval|maintenance\s+schedule|periodic\s+maintenance|odometer|months?|km\s*x\s*1000|miles?\s*x\s*1000|every\s+\d+|inspect|replace\s+every)\b",
    re.IGNORECASE,
)
_WEAR_LIMIT_RE = re.compile(
    r"\b(?:wear\s+limit|service\s+limit|max(?:imum)?\s+wear|maximum\s+play|runout\s+limit|distortion\s+limit)\b",
    re.IGNORECASE,
)
_BEARING_CLEARANCE_RE = re.compile(
    r"\b(?:bearing|journal|crankshaft|connecting\s+rod|oil\s+clearance|bearing\s+grade|bearing\s+color|color\s+code|thickness\s+code|bearing\s+selection)\b",
    re.IGNORECASE,
)
_FLUID_CAPACITY_RE = re.compile(
    r"\b(?:fluid|capacity|capacities|engine\s+oil|coolant|refrigerant|transmission\s+oil|brake\s+fluid|dry\s+fill|refill|liters?|quarts?|viscosity)\b",
    re.IGNORECASE,
)
_ELECTRICAL_RE = re.compile(
    r"\b(?:resistance|voltage|current|terminal|pin\s+no|wire\s+color|sensor|actuator|k?ω|k?ohm|m?v|m?a|battery|alternator|fuse)\b",
    re.IGNORECASE,
)
_TIGHTENING_SEQ_RE = re.compile(
    r"\b(?:tightening\s+sequence|tightening\s+order|step\s+1|step\s+2|step\s+3|angle\s+tightening|torque\s+turn)\b",
    re.IGNORECASE,
)
_DIAGNOSTIC_RE = re.compile(
    r"\b(?:dtc|diagnostic\s+trouble\s+code|trouble\s+code|symptom|probable\s+cause|diagnostic\s+step|malfunction|check\s+item)\b",
    re.IGNORECASE,
)
_STANDARD_SPEC_RE = re.compile(
    r"\b(?:standard|nominal|specification|dimension|clearance|play|gap|deflection|stroke|backlash)\b",
    re.IGNORECASE,
)


class AutomotiveTableClassifier:
    """Deterministic classifier assigning AutomotiveTableType based on title, headers, and cell tokens."""

    @classmethod
    def classify(
        cls,
        title: str | None,
        header_names: Sequence[str],
        sample_cells: Sequence[str],
    ) -> AutomotiveTableType:
        """Classify a table into one of 10 AutomotiveTableType categories."""
        combined_title = title or ""
        combined_headers = " ".join(header_names)
        combined_cells = " ".join(sample_cells[:50])  # Sample first 50 cells for classification
        full_text = f"{combined_title} {combined_headers} {combined_cells}".lower()

        # 1. Check title for high-confidence primary signals
        title_lower = combined_title.lower()
        if _TIGHTENING_SEQ_RE.search(title_lower):
            return AutomotiveTableType.TIGHTENING_SEQUENCE
        if _SERVICE_INTERVAL_RE.search(title_lower):
            return AutomotiveTableType.SERVICE_INTERVAL
        if _BEARING_CLEARANCE_RE.search(title_lower):
            return AutomotiveTableType.BEARING_CLEARANCE
        if _FLUID_CAPACITY_RE.search(title_lower):
            return AutomotiveTableType.FLUID_CAPACITY
        if _ELECTRICAL_RE.search(title_lower):
            return AutomotiveTableType.ELECTRICAL_SPECIFICATION
        if _DIAGNOSTIC_RE.search(title_lower):
            return AutomotiveTableType.DIAGNOSTIC_LOOKUP
        if _WEAR_LIMIT_RE.search(title_lower):
            return AutomotiveTableType.WEAR_LIMIT
        if _TORQUE_RE.search(title_lower):
            return AutomotiveTableType.TORQUE_SPECIFICATION

        # 2. Check column headers
        headers_lower = combined_headers.lower()
        if _TIGHTENING_SEQ_RE.search(headers_lower):
            return AutomotiveTableType.TIGHTENING_SEQUENCE
        if _SERVICE_INTERVAL_RE.search(headers_lower):
            return AutomotiveTableType.SERVICE_INTERVAL
        if _BEARING_CLEARANCE_RE.search(headers_lower):
            return AutomotiveTableType.BEARING_CLEARANCE
        if _FLUID_CAPACITY_RE.search(headers_lower):
            return AutomotiveTableType.FLUID_CAPACITY
        if _ELECTRICAL_RE.search(headers_lower):
            return AutomotiveTableType.ELECTRICAL_SPECIFICATION
        if _DIAGNOSTIC_RE.search(headers_lower):
            return AutomotiveTableType.DIAGNOSTIC_LOOKUP
        if _WEAR_LIMIT_RE.search(headers_lower):
            return AutomotiveTableType.WEAR_LIMIT
        if _TORQUE_RE.search(headers_lower):
            return AutomotiveTableType.TORQUE_SPECIFICATION
        if _STANDARD_SPEC_RE.search(headers_lower):
            return AutomotiveTableType.STANDARD_SPECIFICATION

        # 3. Check full text token distribution
        if _TORQUE_RE.search(full_text):
            return AutomotiveTableType.TORQUE_SPECIFICATION
        if _WEAR_LIMIT_RE.search(full_text):
            return AutomotiveTableType.WEAR_LIMIT
        if _BEARING_CLEARANCE_RE.search(full_text):
            return AutomotiveTableType.BEARING_CLEARANCE
        if _FLUID_CAPACITY_RE.search(full_text):
            return AutomotiveTableType.FLUID_CAPACITY
        if _ELECTRICAL_RE.search(full_text):
            return AutomotiveTableType.ELECTRICAL_SPECIFICATION
        if _DIAGNOSTIC_RE.search(full_text):
            return AutomotiveTableType.DIAGNOSTIC_LOOKUP
        if _SERVICE_INTERVAL_RE.search(full_text):
            return AutomotiveTableType.SERVICE_INTERVAL
        if _STANDARD_SPEC_RE.search(full_text):
            return AutomotiveTableType.STANDARD_SPECIFICATION

        # 4. Default fallback
        return AutomotiveTableType.GENERAL_SPECIFICATION
