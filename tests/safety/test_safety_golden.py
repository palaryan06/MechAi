"""Golden tests for safety contracts to enforce immutability and schema."""

import pytest
from pydantic import ValidationError

from mechai.contracts.provenance import BoundingBox, SourceRef
from mechai.contracts.safety import (
    HazardCategory,
    SafetyAdmonition,
    SafetyCondition,
    SafetyConsequence,
    SafetySeverity,
)


class TestSafetyGolden:
    """Golden schema tests for safety engine."""

    def test_immutability(self) -> None:
        """Ensure models are frozen."""
        bbox = BoundingBox(left=0, top=0, right=10, bottom=10)
        prov = SourceRef(page_number=1)
        
        adm = SafetyAdmonition(
            admonition_id="adm_1",
            severity=SafetySeverity.WARNING,
            original_label="WARNING",
            raw_text="Hot!",
            page_span=(1, 1),
            bbox=bbox,
            provenance=prov,
        )
        
        with pytest.raises(ValidationError):
            adm.admonition_id = "new_id"  # type: ignore

    def test_roundtrip_serialization(self) -> None:
        """Ensure json serialization works cleanly."""
        bbox = BoundingBox(left=0, top=0, right=10, bottom=10)
        prov = SourceRef(page_number=1)
        
        cond = SafetyCondition(
            condition_id="cond_1",
            text="when engine is hot",
            confidence=0.9,
            provenance=prov,
        )
        
        adm = SafetyAdmonition(
            admonition_id="adm_1",
            severity=SafetySeverity.WARNING,
            original_label="WARNING",
            raw_text="Hot!",
            conditions=(cond,),
            page_span=(1, 1),
            bbox=bbox,
            provenance=prov,
        )
        
        data = adm.model_dump()
        rehydrated = SafetyAdmonition.model_validate(data)
        
        assert rehydrated.admonition_id == "adm_1"
        assert len(rehydrated.conditions) == 1
        assert rehydrated.conditions[0].text == "when engine is hot"
