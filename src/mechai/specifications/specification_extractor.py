"""Extracts generic specifications (clearances, limits, capacities) from text and tables."""

from __future__ import annotations

import re
import uuid

from mechai.contracts.specifications import AutomotiveSpecificationFact, SpecificationType
from mechai.contracts.provenance import SourceRef
from mechai.specifications.config import SpecificationConfig
from mechai.specifications.unit_normalizer import UnitNormalizer
from mechai.specifications.condition_parser import ConditionParser


class SpecificationExtractor:
    """Deterministically extracts Specification facts from raw text and structures."""

    def __init__(self, config: SpecificationConfig | None = None) -> None:
        """Initialize the SpecificationExtractor."""
        self._config = config or SpecificationConfig()
        self._normalizer = UnitNormalizer(self._config)
        self._condition_parser = ConditionParser(self._config)

    def _generate_id(self) -> str:
        """Generate a deterministic-like unique ID for the fact."""
        return f"fact_sp_{uuid.uuid4().hex[:8]}"

    def _determine_fact_type(self, canonical_unit: str | None) -> SpecificationType:
        """Determine SpecificationType based on the canonical unit."""
        if not canonical_unit:
            return SpecificationType.OTHER
        if canonical_unit == "N.m":
            return SpecificationType.TORQUE
        if canonical_unit == "mm":
            return SpecificationType.CLEARANCE  # Or DIMENSION depending on context, default to CLEARANCE for MVP
        if canonical_unit == "L":
            return SpecificationType.CAPACITY
        if canonical_unit == "kPa":
            return SpecificationType.PRESSURE
        if canonical_unit == "C":
            return SpecificationType.TEMPERATURE
        if canonical_unit in {"V", "A", "ohm"}:
            if canonical_unit == "V":
                return SpecificationType.VOLTAGE
            if canonical_unit == "A":
                return SpecificationType.OTHER
            if canonical_unit == "ohm":
                return SpecificationType.RESISTANCE
        return SpecificationType.OTHER

    def extract_from_text(
        self, 
        text: str, 
        source_ref: SourceRef, 
        target_override: str | None = None
    ) -> list[AutomotiveSpecificationFact]:
        """Extract multiple specification facts from a single string."""
        facts: list[AutomotiveSpecificationFact] = []
        
        # Clean footnote references
        clean_text = self._config.footnote_strip_pattern.sub("", text)
        
        # Find all value-with-unit matches
        matches = list(self._config.value_with_unit_pattern.finditer(clean_text))
        
        for match in matches:
            full_match = match.group(0)
            
            spec_value = self._normalizer.extract_specification_value(full_match)
            if not spec_value:
                continue
                
            # Skip if it's torque (that should be handled by TorqueExtractor)
            if spec_value.canonical_unit == "N.m":
                continue
                
            meas_cond = self._condition_parser.extract_operating_condition(clean_text)
            
            target = target_override
            if not target:
                target_match = re.search(r"([A-Za-z\s\-]+?)\s*(?:is\s+|to\s+|:\s*|\s+)" + re.escape(full_match), clean_text)
                if target_match:
                    target = target_match.group(1).strip()
                    
            if spec_value.canonical_unit is None and not target:
                continue

            fact = AutomotiveSpecificationFact(
                id=self._generate_id(),
                fact_type=self._determine_fact_type(spec_value.canonical_unit),
                target_component=target,
                value=spec_value,
                measurement_condition=meas_cond,
                evidence=(source_ref,)
            )
            facts.append(fact)
            
        return facts
