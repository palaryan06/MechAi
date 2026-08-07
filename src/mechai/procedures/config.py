"""Configuration definitions for Automotive Procedure Intelligence Engine (RFC-AUTO-002)."""

from __future__ import annotations

import re
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field


class ProcedureEngineConfig(BaseModel):
    """Calibrated configuration and regex patterns for procedural knowledge extraction."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    # Step numbering detection patterns
    step_numbered_regex: str = r"^(?:\(?(\d+)[.\)]|\b(\d+)\))\s+(.*)$"
    step_alpha_regex: str = r"^(?:\(?([a-zA-Z])[.\)]|\b([a-zA-Z])\))\s+(.*)$"
    step_roman_regex: str = r"^(?:\(?([ivxlcdmIVXLCDM]+)[.\)]|\b([ivxlcdmIVXLCDM]+)\))\s+(.*)$"
    step_bullet_regex: str = r"^([•\-\*▪\u2022\u2023\u25E6\u2043\u2219])\s+(.*)$"

    # Action headings for procedure boundary detection
    procedure_action_verbs: tuple[str, ...] = (
        "removal",
        "installation",
        "replacement",
        "disassembly",
        "reassembly",
        "assembly",
        "inspection",
        "adjustment",
        "overhaul",
        "maintenance",
        "bleeding",
        "calibration",
        "testing",
        "servicing",
        "check",
        "troubleshooting",
        "diagnosis",
    )

    # Special Service Tool (SST) detection patterns
    sst_regexes: tuple[str, ...] = (
        r"(?:SST[:\s]+)?\b(099\d{2}[-\s]?\d{5})\b",
        r"(?:SST\s*(?:No\.?)?\s*[:\s]*)([A-Z0-9]+-[A-Z0-9]+)",
        r"(?:Special\s+Service\s+Tool\s*(?:No\.?)?\s*[:\s]*)([A-Z0-9]+-[A-Z0-9]+)",
        r"\b(SST\s*[A-Z0-9\-]+)\b",
    )

    # Standard tool keywords
    tool_keywords: tuple[str, ...] = (
        "torque wrench",
        "feeler gauge",
        "dial indicator",
        "micrometer",
        "vernier caliper",
        "caliper",
        "piston ring compressor",
        "piston ring expander",
        "valve spring compressor",
        "bearing puller",
        "bearing installer",
        "oil seal installer",
        "seal remover",
        "socket wrench",
        "hex wrench",
        "torx",
        "allen wrench",
        "breaker bar",
        "impact wrench",
        "multimeter",
        "scan tool",
        "compression tester",
        "pressure gauge",
        "vacuum pump",
        "timing light",
    )

    # Material & Consumable keywords
    material_keywords: tuple[str, ...] = (
        "suzuki bond",
        "threebond",
        "loctite",
        "thread locker",
        "threadlocker",
        "silicone sealant",
        "liquid gasket",
        "gasket sealant",
        "engine oil",
        "clean engine oil",
        "gear oil",
        "brake fluid",
        "coolant",
        "antifreeze",
        "lithium grease",
        "molybdenum grease",
        "chassis grease",
        "anti-seize",
        "brake cleaner",
    )

    # Mandatory replacement indicators
    mandatory_replacement_keywords: tuple[str, ...] = (
        "do not reuse",
        "replace with new",
        "always replace",
        "use a new",
        "new gasket",
        "new o-ring",
        "new cotter pin",
        "new lock washer",
        "new oil seal",
        "new snap ring",
    )

    # Cross-reference patterns
    table_ref_regex: str = r"(?:(?:Refer\s+to\s+)?Table\s+([A-Z0-9\-]+)|torque\s+specifications?\s+table|wear\s+limit\s+table)"
    figure_ref_regex: str = r"(?:Fig\.?|Figure|Illustration)\s*([0-9]+[A-Z]?(?:[-.][0-9]+[A-Z]?)?)"
    callout_ref_regex: str = r"\[([A-Z0-9])\]|\(([0-9]{1,2})\)"
    page_ref_regex: str = r"(?:page|p\.)\s*([0-9]+(?:[-.][0-9]+)?)"

    # Admonition matching patterns
    admonition_prefix_regex: str = r"^(WARNING|CAUTION|NOTE|DANGER|NOTICE)\s*:\s*(.*)$"

    # Multi-page continuation markers
    continuation_title_markers: tuple[str, ...] = (
        "(continued)",
        "(cont'd)",
        "- continued",
        "(cont.)",
    )

    # Minimum confidence
    min_confidence: float = 0.90
