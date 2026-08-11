"""Tests for generic specification extraction logic."""

import pytest

from mechai.specifications.specification_extractor import SpecificationExtractor
from mechai.contracts.specifications import SpecificationType
from mechai.contracts.provenance import SourceRef


class TestSpecificationExtraction:
    """Ensure specification facts are extracted correctly."""

    @pytest.fixture
    def extractor(self) -> SpecificationExtractor:
        return SpecificationExtractor()

    def test_extract_clearance(self, extractor: SpecificationExtractor) -> None:
        """Test extraction of a clearance value."""
        text = "Valve clearance IN is 0.13 - 0.17 mm when cold."
        ref = SourceRef(page_number=1)
        facts = extractor.extract_from_text(text, ref)
        
        assert len(facts) == 1
        fact = facts[0]
        assert fact.fact_type == SpecificationType.CLEARANCE
        assert fact.target_component == "Valve clearance IN"
        assert fact.value.tolerance_min == 0.13
        assert fact.value.tolerance_max == 0.17
        assert fact.value.canonical_unit == "mm"
        assert fact.measurement_condition == "when cold"

    def test_extract_capacity(self, extractor: SpecificationExtractor) -> None:
        """Test extraction of a fluid capacity."""
        text = "Engine oil capacity: 2.9 L"
        ref = SourceRef(page_number=1)
        facts = extractor.extract_from_text(text, ref)
        
        assert len(facts) == 1
        fact = facts[0]
        assert fact.fact_type == SpecificationType.CAPACITY
        assert fact.target_component == "Engine oil capacity"
        assert fact.value.numeric_value == 2.9
        assert fact.value.canonical_unit == "L"

    def test_ignore_torque(self, extractor: SpecificationExtractor) -> None:
        """Ensure torques are ignored by the specification extractor."""
        text = "Tighten to 45 N.m"
        ref = SourceRef(page_number=1)
        facts = extractor.extract_from_text(text, ref)
        assert len(facts) == 0
