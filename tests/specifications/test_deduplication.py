"""Tests for fact deduplication."""

import pytest

from mechai.specifications.deduplication import FactDeduplicator
from mechai.contracts.specifications import (
    AutomotiveTorqueFact,
    SpecificationValue,
)
from mechai.contracts.provenance import SourceRef, ExtractionMethod


class TestDeduplication:
    """Ensure identical facts are merged and their evidence combined."""

    @pytest.fixture
    def deduplicator(self) -> FactDeduplicator:
        return FactDeduplicator()

    def test_merge_identical_torques(self, deduplicator: FactDeduplicator) -> None:
        """Merge identical torque facts."""
        ref1 = SourceRef(page_number=1, extraction_method=ExtractionMethod.RULE)
        ref2 = SourceRef(page_number=2, extraction_method=ExtractionMethod.HEURISTIC)
        
        f1 = AutomotiveTorqueFact(
            id="t1",
            target_component="Wheel lug nut",
            value=SpecificationValue(raw_value="85 N.m", numeric_value=85.0, canonical_value=85.0),
            evidence=(ref1,)
        )
        f2 = AutomotiveTorqueFact(
            id="t2",
            target_component="Wheel lug nut",
            value=SpecificationValue(raw_value="85 N.m", numeric_value=85.0, canonical_value=85.0),
            evidence=(ref2,)
        )
        
        merged = deduplicator.deduplicate([f1, f2])
        
        assert len(merged) == 1
        assert len(merged[0].evidence) == 2
        assert ref1 in merged[0].evidence
        assert ref2 in merged[0].evidence

    def test_do_not_merge_different_values(self, deduplicator: FactDeduplicator) -> None:
        """Ensure different facts are kept separate."""
        ref1 = SourceRef(page_number=1)
        
        f1 = AutomotiveTorqueFact(
            id="t1",
            target_component="Wheel lug nut",
            value=SpecificationValue(raw_value="85 N.m", numeric_value=85.0, canonical_value=85.0),
            evidence=(ref1,)
        )
        f2 = AutomotiveTorqueFact(
            id="t2",
            target_component="Wheel lug nut",
            value=SpecificationValue(raw_value="100 N.m", numeric_value=100.0, canonical_value=100.0),
            evidence=(ref1,)
        )
        
        merged = deduplicator.deduplicate([f1, f2])
        
        assert len(merged) == 2
