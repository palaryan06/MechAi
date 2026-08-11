"""Tests for the canonical specification contracts."""

import pytest
from pydantic import ValidationError

from mechai.contracts.specifications import (
    ApplicabilityContext,
    AutomotiveSpecificationFact,
    AutomotiveSpecificationSet,
    AutomotiveTorqueFact,
    SpecificationType,
    SpecificationValue,
)
from mechai.contracts.provenance import SourceRef, ExtractionMethod


class TestSpecificationContracts:
    """Test the frozen immutable contracts."""

    def test_immutability(self) -> None:
        """Ensure contracts are immutable and frozen."""
        spec_val = SpecificationValue(
            raw_value="45 N.m",
            numeric_value=45.0,
            original_unit="N.m",
            canonical_value=45.0,
            canonical_unit="N.m"
        )
        
        with pytest.raises(ValidationError):
            spec_val.raw_value = "50 N.m"  # type: ignore

        app = ApplicabilityContext(engine_code="K10B")
        with pytest.raises(ValidationError):
            app.engine_code = "F8D"  # type: ignore

    def test_applicability_context_defaults(self) -> None:
        """Ensure applicability defaults to None for universal facts."""
        app = ApplicabilityContext()
        assert app.engine_code is None
        assert app.transmission is None

    def test_torque_fact_creation(self) -> None:
        """Test creating a valid torque fact."""
        ref = SourceRef(page_number=1, extraction_method=ExtractionMethod.RULE)
        spec_val = SpecificationValue(raw_value="45 N.m")
        app = ApplicabilityContext(engine_code="F8D")
        
        fact = AutomotiveTorqueFact(
            id="tq1",
            target_component="Cylinder head bolt",
            value=spec_val,
            applicability=app,
            evidence=(ref,)
        )
        
        assert fact.fact_type == SpecificationType.TORQUE
        assert fact.target_component == "Cylinder head bolt"
        assert fact.applicability.engine_code == "F8D"
        assert len(fact.evidence) == 1

    def test_specification_set(self) -> None:
        """Test the top-level specification set container."""
        ref = SourceRef(page_number=1, extraction_method=ExtractionMethod.RULE)
        spec_val = SpecificationValue(raw_value="45 N.m")
        tq = AutomotiveTorqueFact(id="tq1", value=spec_val, evidence=(ref,))
        
        spec_val2 = SpecificationValue(raw_value="0.15 mm")
        sp = AutomotiveSpecificationFact(id="sp1", fact_type=SpecificationType.CLEARANCE, value=spec_val2, evidence=(ref,))
        
        fact_set = AutomotiveSpecificationSet(
            document_id="doc1",
            torques=(tq,),
            specifications=(sp,)
        )
        
        assert fact_set.total_facts == 2
        assert fact_set.total_conflicts == 0
