"""Tests for conflict detection logic."""

import pytest

from mechai.specifications.conflict_detector import ConflictDetector
from mechai.contracts.specifications import (
    AutomotiveTorqueFact,
    SpecificationValue,
    ConflictCategory,
    ApplicabilityContext,
)
from mechai.domain.enums import FastenerCondition


class TestConflictDetection:
    """Ensure conflicts between facts are detected correctly."""

    @pytest.fixture
    def detector(self) -> ConflictDetector:
        return ConflictDetector()

    def test_no_conflict_different_targets(self, detector: ConflictDetector) -> None:
        """Ensure different components don't conflict."""
        f1 = AutomotiveTorqueFact(
            id="t1",
            target_component="Cylinder head bolt",
            value=SpecificationValue(raw_value="45 N.m", canonical_value=45.0)
        )
        f2 = AutomotiveTorqueFact(
            id="t2",
            target_component="Main bearing bolt",
            value=SpecificationValue(raw_value="60 N.m", canonical_value=60.0)
        )
        
        conflicts = detector.detect_conflicts([f1, f2])
        assert len(conflicts) == 0

    def test_value_conflict(self, detector: ConflictDetector) -> None:
        """Ensure different values for the same component trigger a conflict."""
        f1 = AutomotiveTorqueFact(
            id="t1",
            target_component="Oil pan bolt",
            value=SpecificationValue(raw_value="10 N.m", canonical_value=10.0)
        )
        f2 = AutomotiveTorqueFact(
            id="t2",
            target_component="Oil pan bolt",
            value=SpecificationValue(raw_value="15 N.m", canonical_value=15.0)
        )
        
        conflicts = detector.detect_conflicts([f1, f2])
        assert len(conflicts) == 1
        assert conflicts[0].category == ConflictCategory.VALUE_CONFLICT
        assert conflicts[0].fact_a_id == "t1"
        assert conflicts[0].fact_b_id == "t2"

    def test_applicability_conflict(self, detector: ConflictDetector) -> None:
        """Ensure same component but different applicability is flagged."""
        f1 = AutomotiveTorqueFact(
            id="t1",
            target_component="Flywheel bolt",
            value=SpecificationValue(raw_value="45 N.m", canonical_value=45.0),
            applicability=ApplicabilityContext(transmission="M/T")
        )
        f2 = AutomotiveTorqueFact(
            id="t2",
            target_component="Flywheel bolt",
            value=SpecificationValue(raw_value="45 N.m", canonical_value=45.0),
            applicability=ApplicabilityContext(transmission="A/T")
        )
        
        conflicts = detector.detect_conflicts([f1, f2])
        assert len(conflicts) == 1
        assert conflicts[0].category == ConflictCategory.APPLICABILITY_CONFLICT

    def test_condition_conflict(self, detector: ConflictDetector) -> None:
        """Ensure different fastener conditions trigger a conflict."""
        f1 = AutomotiveTorqueFact(
            id="t1",
            target_component="Connecting rod bolt",
            value=SpecificationValue(raw_value="35 N.m", canonical_value=35.0),
            fastener_condition=FastenerCondition.DRY
        )
        f2 = AutomotiveTorqueFact(
            id="t2",
            target_component="Connecting rod bolt",
            value=SpecificationValue(raw_value="35 N.m", canonical_value=35.0),
            fastener_condition=FastenerCondition.OIL_LUBRICATED
        )
        
        conflicts = detector.detect_conflicts([f1, f2])
        assert len(conflicts) == 1
        assert conflicts[0].category == ConflictCategory.CONDITION_CONFLICT
