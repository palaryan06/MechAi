"""Unit Normalization Subsystem."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from mechai.contracts.specifications import SpecificationValue
from mechai.specifications.config import SpecificationConfig, UnitNormalizationRule


@dataclass(frozen=True)
class NormalizationResult:
    """Result of attempting to normalize a unit and its value."""
    normalized_value: float | None
    normalized_unit: str | None
    tolerance_min: float | None = None
    tolerance_max: float | None = None


class UnitNormalizer:
    """Deterministically normalizes specification values to SI canonical units."""

    def __init__(self, config: SpecificationConfig | None = None) -> None:
        """Initialize the UnitNormalizer."""
        self._config = config or SpecificationConfig()

    def _find_rule(self, raw_unit: str | None) -> UnitNormalizationRule | None:
        """Find the matching normalization rule for a given raw unit string."""
        if not raw_unit:
            return None
        raw_unit_stripped = raw_unit.strip()
        for rule in self._config.unit_rules:
            if rule.regex_pattern.match(raw_unit_stripped):
                return rule
        return None

    def _parse_value_string(self, raw_value: str) -> tuple[float | None, float | None, float | None]:
        """Parse numeric values, ranges, or tolerances from a string.
        
        Returns:
            Tuple of (numeric_value, tolerance_min, tolerance_max).
            For ranges, numeric_value is None, but min/max are populated.
            For simple values, numeric_value is populated, min/max are None.
        """
        # Check tolerance first (e.g. "45 +/- 2")
        tol_match = self._config.tolerance_pattern.match(raw_value.strip())
        if tol_match:
            base_val = float(tol_match.group(1))
            tol_val = float(tol_match.group(2))
            return base_val, base_val - tol_val, base_val + tol_val

        # Check range (e.g. "45-50")
        range_match = self._config.range_pattern.match(raw_value.strip())
        if range_match:
            min_val = float(range_match.group(1))
            max_val = float(range_match.group(2))
            return None, min_val, max_val

        # Check single numeric value
        num_match = self._config.numeric_pattern.match(raw_value.strip())
        if num_match:
            return float(num_match.group(0)), None, None

        return None, None, None

    def normalize(self, raw_value_str: str, raw_unit_str: str) -> NormalizationResult:
        """Normalize a value and unit to canonical representation."""
        rule = self._find_rule(raw_unit_str)
        if not rule:
            # If no rule matches, we cannot normalize the unit. 
            # We still try to extract the numeric value.
            numeric, t_min, t_max = self._parse_value_string(raw_value_str)
            return NormalizationResult(
                normalized_value=numeric,
                normalized_unit=None,
                tolerance_min=t_min,
                tolerance_max=t_max
            )
        
        numeric, t_min, t_max = self._parse_value_string(raw_value_str)
        
        normalized_numeric = numeric * rule.conversion_factor if numeric is not None else None
        normalized_min = t_min * rule.conversion_factor if t_min is not None else None
        normalized_max = t_max * rule.conversion_factor if t_max is not None else None
        
        return NormalizationResult(
            normalized_value=normalized_numeric,
            normalized_unit=rule.canonical_unit,
            tolerance_min=normalized_min,
            tolerance_max=normalized_max
        )

    def extract_specification_value(self, full_text: str) -> SpecificationValue | None:
        """Extract a SpecificationValue from a full text string (e.g. '45 N.m')."""
        match = self._config.value_with_unit_pattern.search(full_text)
        if not match:
            # Maybe it's just a number without a unit.
            num_match = self._config.numeric_pattern.search(full_text.strip())
            if num_match:
                raw_val = num_match.group(0)
                numeric, t_min, t_max = self._parse_value_string(raw_val)
                return SpecificationValue(
                    raw_value=full_text.strip(),
                    numeric_value=numeric,
                    tolerance_min=t_min,
                    tolerance_max=t_max
                )
            return None

        raw_val = match.group(1)
        raw_unit = match.group(2)
        
        norm_result = self.normalize(raw_val, raw_unit)
        numeric, _, _ = self._parse_value_string(raw_val)
        
        return SpecificationValue(
            raw_value=match.group(0).strip(),
            numeric_value=numeric,
            original_unit=raw_unit.strip() if raw_unit else None,
            canonical_value=norm_result.normalized_value,
            canonical_unit=norm_result.normalized_unit,
            tolerance_min=norm_result.tolerance_min,
            tolerance_max=norm_result.tolerance_max
        )
