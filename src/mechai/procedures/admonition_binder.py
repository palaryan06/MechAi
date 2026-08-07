"""Admonition Binder for Automotive Procedure Intelligence Engine (RFC-AUTO-002).

Binds safety warnings, cautions, danger alerts, and technical notes to the exact
procedure steps they modify based on reading order sequence and spatial layout.
"""

from __future__ import annotations

import re

from mechai.contracts.layout import RegionType
from mechai.contracts.ordering import OrderedLayoutRegion
from mechai.contracts.procedures import AdmonitionType, BoundAdmonition
from mechai.procedures.config import ProcedureEngineConfig


class AdmonitionBinder:
    """Deterministic binder for safety admonitions and technical notes."""

    def __init__(self, config: ProcedureEngineConfig | None = None) -> None:
        self._config = config or ProcedureEngineConfig()
        self._re_prefix = re.compile(self._config.admonition_prefix_regex, re.IGNORECASE)

    def extract_admonitions_from_region(self, region: OrderedLayoutRegion) -> list[BoundAdmonition]:
        """Extract one or more BoundAdmonition objects from an OrderedLayoutRegion."""
        admonitions: list[BoundAdmonition] = []
        text = region.text.strip()
        if not text:
            return []

        # 1. Classified Layout Region (WARNING_BOX or NOTE_BOX)
        if region.region_type == RegionType.WARNING_BOX:
            adm_type = self._classify_severity(text, default=AdmonitionType.WARNING)
            admonitions.append(
                BoundAdmonition(
                    admonition_id=f"adm_{region.id}",
                    admonition_type=adm_type,
                    text=text,
                    bbox=region.bbox,
                    page_number=region.page_number,
                    region_id=region.id,
                    provenance=region.provenance,
                )
            )
            return admonitions

        if region.region_type == RegionType.NOTE_BOX:
            adm_type = self._classify_severity(text, default=AdmonitionType.NOTE)
            admonitions.append(
                BoundAdmonition(
                    admonition_id=f"adm_{region.id}",
                    admonition_type=adm_type,
                    text=text,
                    bbox=region.bbox,
                    page_number=region.page_number,
                    region_id=region.id,
                    provenance=region.provenance,
                )
            )
            return admonitions

        # 2. Inline Admonitions within regular paragraph/body text
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        for idx, line in enumerate(lines):
            m = self._re_prefix.match(line)
            if m:
                tag = m.group(1).upper()
                msg = m.group(2).strip()
                adm_type = self._tag_to_type(tag)
                admonitions.append(
                    BoundAdmonition(
                        admonition_id=f"adm_{region.id}_{idx}",
                        admonition_type=adm_type,
                        text=f"{tag}: {msg}" if msg else line,
                        bbox=region.bbox,
                        page_number=region.page_number,
                        region_id=region.id,
                        provenance=region.provenance,
                    )
                )

        return admonitions

    def _classify_severity(self, text: str, default: AdmonitionType) -> AdmonitionType:
        """Classify admonition severity from text keywords."""
        upper = text[:60].upper()
        if "DANGER" in upper:
            return AdmonitionType.DANGER
        if "WARNING" in upper:
            return AdmonitionType.WARNING
        if "CAUTION" in upper:
            return AdmonitionType.CAUTION
        if "NOTICE" in upper:
            return AdmonitionType.NOTICE
        if "NOTE" in upper:
            return AdmonitionType.NOTE
        return default

    def _tag_to_type(self, tag: str) -> AdmonitionType:
        """Map text prefix string to AdmonitionType enum."""
        mapping = {
            "DANGER": AdmonitionType.DANGER,
            "WARNING": AdmonitionType.WARNING,
            "CAUTION": AdmonitionType.CAUTION,
            "NOTICE": AdmonitionType.NOTICE,
            "NOTE": AdmonitionType.NOTE,
        }
        return mapping.get(tag, AdmonitionType.NOTE)
