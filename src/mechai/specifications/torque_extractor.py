"""Extracts torque specifications from text and tables."""

from __future__ import annotations

import re
import uuid

from mechai.contracts.specifications import AutomotiveTorqueFact, SpecificationType
from mechai.contracts.provenance import SourceRef, ExtractionMethod
from mechai.specifications.config import SpecificationConfig
from mechai.specifications.unit_normalizer import UnitNormalizer
from mechai.specifications.condition_parser import ConditionParser


class TorqueExtractor:
    """Deterministically extracts Torque facts from raw text and structures."""

    def __init__(self, config: SpecificationConfig | None = None) -> None:
        """Initialize the TorqueExtractor."""
        self._config = config or SpecificationConfig()
        self._normalizer = UnitNormalizer(self._config)
        self._condition_parser = ConditionParser(self._config)
        
        # Heuristic keywords indicating torque
        self._torque_keywords = ("torque", "tighten", "tightening")

    def _generate_id(self) -> str:
        """Generate a deterministic-like unique ID for the fact."""
        return f"fact_tq_{uuid.uuid4().hex[:8]}"
        
    def _extract_angle(self, text: str) -> float | None:
        """Extract tightening angle (e.g. + 90°)."""
        match = self._config.angle_pattern.search(text)
        if match:
            return float(match.group(1))
        return None

    def _is_likely_torque(self, text: str, unit: str | None) -> bool:
        """Determine if a raw string is likely a torque specification."""
        if unit:
            unit_lower = unit.lower()
            if unit_lower in {"to", "and", "the", "of", "for", "in", "is", "are"}:
                return False
            if unit_lower in {"n.m", "n-m", "nm", "n·m", "kgf.m", "kgf-m", "kg-m", "kgm", "ft-lb", "ft.lb", "lb-ft", "in-lb"}:
                return True
            
        lower_text = text.lower()
        if any(kw in lower_text for kw in self._torque_keywords):
            return True
            
        return False

    def extract_from_text(
        self, 
        text: str, 
        source_ref: SourceRef, 
        target_override: str | None = None
    ) -> list[AutomotiveTorqueFact]:
        """Extract multiple torque facts from a single string (e.g. a procedure step)."""
        facts: list[AutomotiveTorqueFact] = []
        
        # 1. Clean footnote references which might look like numbers
        clean_text = self._config.footnote_strip_pattern.sub("", text)
        
        # 2. Find all value-with-unit matches
        matches = list(self._config.value_with_unit_pattern.finditer(clean_text))
        
        for match in matches:
            raw_val = match.group(1)
            raw_unit = match.group(2)
            full_match = match.group(0)
            
            if not self._is_likely_torque(clean_text, raw_unit):
                continue
                
            spec_value = self._normalizer.extract_specification_value(full_match)
            if not spec_value:
                continue
                
            if spec_value.canonical_unit != "N.m":
                if spec_value.canonical_unit is not None:
                    # It's a valid measurement, but not torque (e.g., clearance)
                    continue
                if spec_value.original_unit and spec_value.original_unit.lower() not in {"n.m", "n-m", "nm", "n·m", "kgf.m", "kgf-m", "kg-m", "kgm", "ft-lb", "ft.lb", "lb-ft", "in-lb"}:
                    # It has some text after it that wasn't recognized as a unit at all (e.g., a random word). Reject it.
                    continue
                
            angle = self._extract_angle(clean_text)
            
            # Skip if this value is actually the angle
            if spec_value.canonical_unit is None and spec_value.numeric_value == angle:
                continue
            fastener_cond = self._condition_parser.extract_fastener_condition(clean_text)
            
            # Simple heuristic: assume target is the noun before the torque
            target = target_override
            if not target:
                # E.g. "cylinder head bolt" in "Tighten cylinder head bolt to 45 N.m"
                target_match = re.search(r"([A-Za-z\s\-]+?)\s+(?:to\s+)?" + re.escape(full_match), clean_text)
                if target_match:
                    target_candidate = target_match.group(1).strip()
                    # Filter out verbs
                    words = target_candidate.split()
                    if words and words[0].lower() in {"tighten", "the", "and"}:
                        target_candidate = " ".join(words[1:])
                    if target_candidate:
                        target = target_candidate

            fact = AutomotiveTorqueFact(
                id=self._generate_id(),
                target_component=target,
                value=spec_value,
                tightening_angle_degrees=angle,
                fastener_condition=fastener_cond,
                evidence=(source_ref,)
            )
            facts.append(fact)
            
        return facts
