"""Boundary Detector for Automotive Procedure Intelligence Engine (RFC-AUTO-002).

Detects procedure start titles, categorizes repair domain taxonomy, extracts
preconditions, postconditions, estimated labor times, and difficulty metrics.
"""

from __future__ import annotations

import re

from mechai.contracts.layout import RegionType
from mechai.contracts.ordering import OrderedLayoutRegion
from mechai.contracts.procedures import ProcedureCategory
from mechai.procedures.config import ProcedureEngineConfig


class BoundaryDetector:
    """Deterministic boundary detector and metadata extractor for repair procedures."""

    def __init__(self, config: ProcedureEngineConfig | None = None) -> None:
        self._config = config or ProcedureEngineConfig()

    def is_procedure_heading(self, region: OrderedLayoutRegion) -> bool:
        """Determine if a region represents a procedure initiation heading."""
        if region.region_type not in (RegionType.HEADING, RegionType.TITLE, RegionType.SUBHEADING):
            return False

        text_lower = region.text.lower()
        # Check action verbs
        for verb in self._config.procedure_action_verbs:
            if re.search(r"\b" + re.escape(verb) + r"\b", text_lower):
                return True

        return False

    def classify_category(self, title: str) -> ProcedureCategory:
        """Classify procedure into domain category based on title keywords."""
        lower = title.lower()

        if "overhaul" in lower:
            return ProcedureCategory.OVERHAUL
        if any(w in lower for w in ("removal", "disassembly", "dismantling", "remove")):
            return ProcedureCategory.REMOVAL_DISASSEMBLY
        if any(w in lower for w in ("installation", "reassembly", "assembly", "install", "mounting")):
            return ProcedureCategory.INSTALLATION_REASSEMBLY
        if any(w in lower for w in ("inspection", "adjustment", "check", "measuring", "testing", "calibration")):
            return ProcedureCategory.INSPECTION_ADJUSTMENT
        if any(w in lower for w in ("maintenance", "bleeding", "service", "replacement", "drain", "refill")):
            return ProcedureCategory.MAINTENANCE
        if any(w in lower for w in ("troubleshooting", "diagnostic", "diagnosis", "symptom")):
            return ProcedureCategory.DIAGNOSTIC_TROUBLESHOOTING

        return ProcedureCategory.GENERAL_PROCEDURE

    def extract_preconditions(self, text: str) -> tuple[str, ...]:
        """Extract explicit pre-procedure requirements and preparation notes."""
        preconditions: list[str] = []
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        for line in lines:
            lower = line.lower()
            if any(
                p in lower
                for p in (
                    "prior to",
                    "before removal",
                    "before starting",
                    "preparation:",
                    "prerequisites:",
                    "disconnect negative",
                    "disconnect battery",
                    "raise vehicle",
                    "drain engine oil",
                    "drain coolant",
                )
            ):
                preconditions.append(line)

        return tuple(preconditions)

    def extract_postconditions(self, text: str) -> tuple[str, ...]:
        """Extract explicit post-procedure verification and reassembly checks."""
        postconditions: list[str] = []
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        for line in lines:
            lower = line.lower()
            if any(
                p in lower
                for p in (
                    "after installation",
                    "after reassembly",
                    "post-service",
                    "refill engine oil",
                    "refill coolant",
                    "check for leaks",
                    "perform road test",
                    "verify operation",
                    "bleed brake system",
                )
            ):
                postconditions.append(line)

        return tuple(postconditions)

    def extract_labor_time_and_difficulty(self, text: str) -> tuple[str | None, str | None]:
        """Extract documented labor time and technician skill/difficulty rating."""
        labor_time: str | None = None
        difficulty: str | None = None

        # Labor time e.g. "Labor Time: 1.5 hr", "Est. Time: 45 min"
        time_match = re.search(
            r"(?:Labor\s+Time|Est\.?\s+Time|Standard\s+Time)[:\s]+([0-9\.]+\s*(?:hr|hours|min|minutes))",
            text,
            re.IGNORECASE,
        )
        if time_match:
            labor_time = time_match.group(1).strip()

        # Difficulty e.g. "Difficulty: Intermediate", "Skill Level: 3/5"
        diff_match = re.search(
            r"(?:Difficulty|Skill\s+Level)[:\s]+(Beginner|Intermediate|Advanced|Expert|[1-5]/5)",
            text,
            re.IGNORECASE,
        )
        if diff_match:
            difficulty = diff_match.group(1).strip()

        return labor_time, difficulty
