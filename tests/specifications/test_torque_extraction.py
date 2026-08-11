"""Tests for torque extraction logic."""

import pytest

from mechai.specifications.torque_extractor import TorqueExtractor
from mechai.contracts.provenance import SourceRef
from mechai.domain.enums import FastenerCondition


class TestTorqueExtraction:
    """Ensure torque facts are extracted correctly from text."""

    @pytest.fixture
    def extractor(self) -> TorqueExtractor:
        return TorqueExtractor()

    def test_extract_simple_torque(self, extractor: TorqueExtractor) -> None:
        """Test extraction of a straightforward torque sentence."""
        text = "Tighten cylinder head bolt to 45 N.m."
        ref = SourceRef(page_number=1)
        facts = extractor.extract_from_text(text, ref)
        
        assert len(facts) == 1
        fact = facts[0]
        assert fact.target_component == "cylinder head bolt"
        assert fact.value.raw_value == "45 N.m"
        assert fact.value.numeric_value == 45.0
        assert fact.value.canonical_unit == "N.m"
        assert fact.fastener_condition == FastenerCondition.DRY
        assert fact.tightening_angle_degrees is None

    def test_extract_torque_with_angle(self, extractor: TorqueExtractor) -> None:
        """Test extraction of torque plus an angle."""
        text = "Tighten the main bearing cap bolt to 45 N.m + 90°."
        ref = SourceRef(page_number=1)
        facts = extractor.extract_from_text(text, ref)
        
        assert len(facts) == 1
        fact = facts[0]
        assert fact.target_component == "the main bearing cap bolt"
        assert fact.value.numeric_value == 45.0
        assert fact.tightening_angle_degrees == 90.0

    def test_extract_torque_with_condition(self, extractor: TorqueExtractor) -> None:
        """Test extraction of torque with a fastener condition."""
        text = "Apply engine oil and tighten bolt to 30 N.m."
        ref = SourceRef(page_number=1)
        facts = extractor.extract_from_text(text, ref)
        
        assert len(facts) == 1
        fact = facts[0]
        assert fact.fastener_condition == FastenerCondition.OIL_LUBRICATED
        assert fact.value.numeric_value == 30.0

    def test_multiple_torques_in_sentence(self, extractor: TorqueExtractor) -> None:
        """Test extracting multiple torques from one string."""
        text = "Tighten bolt A to 20 N.m and bolt B to 40 N.m."
        ref = SourceRef(page_number=1)
        facts = extractor.extract_from_text(text, ref)
        
        assert len(facts) == 2
        assert facts[0].value.numeric_value == 20.0
        assert facts[1].value.numeric_value == 40.0

    def test_ambiguous_number_ignored(self, extractor: TorqueExtractor) -> None:
        """Ensure non-torque numbers are not extracted."""
        text = "Use Model 45 to tighten."
        ref = SourceRef(page_number=1)
        facts = extractor.extract_from_text(text, ref)
        assert len(facts) == 0
