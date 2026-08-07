"""Golden contract tests for Automotive Procedure Intelligence Engine (RFC-AUTO-002).

Validates schema constraints, immutability (frozen=True), and JSON serialization / deserialization.
"""

from __future__ import annotations

import json
import pytest
from pydantic import ValidationError

from mechai.contracts.layout import BoundingBox, ExtractionMethod, SourceRef
from mechai.contracts.procedures import (
    AdmonitionType,
    AutomotiveProcedure,
    AutomotiveProcedureSet,
    BoundAdmonition,
    ProcedureCategory,
    ProcedureStep,
    RequiredMaterial,
    RequiredTool,
    StepNumberingStyle,
)


def _sample_source_ref(page: int = 1) -> SourceRef:
    return SourceRef(
        page_number=page,
        bbox=BoundingBox(left=72.0, top=100.0, right=540.0, bottom=700.0),
        extraction_method=ExtractionMethod.RULE,
        confidence=0.99,
    )


def _sample_procedure_step(
    step_id: str = "step_01",
    seq: int = 1,
    level: int = 0,
    parent_id: str | None = None,
) -> ProcedureStep:
    return ProcedureStep(
        step_id=step_id,
        sequence_number=seq,
        display_number=f"{seq}.",
        numbering_style=StepNumberingStyle.NUMBERED,
        level=level,
        parent_step_id=parent_id,
        child_step_ids=(),
        action_text="Disconnect negative (-) battery cable.",
        bbox=BoundingBox(left=72.0, top=120.0, right=540.0, bottom=140.0),
        page_number=1,
        reading_order_ref="reg_001",
        confidence=0.98,
        provenance=_sample_source_ref(1),
        bound_admonitions=(
            BoundAdmonition(
                admonition_id="adm_01",
                admonition_type=AdmonitionType.CAUTION,
                text="CAUTION: Wait at least 90 seconds after disconnecting battery.",
                bbox=BoundingBox(left=72.0, top=145.0, right=540.0, bottom=165.0),
                page_number=1,
                region_id="reg_adm_01",
                provenance=_sample_source_ref(1),
            ),
        ),
        required_tools=(
            RequiredTool(
                name="SST 09915-64510",
                tool_number="09915-64510",
                is_sst=True,
                confidence=0.98,
            ),
        ),
        required_materials=(
            RequiredMaterial(
                name="Suzuki Bond 1215",
                specification="1215",
                is_replacement_mandatory=False,
                confidence=0.95,
            ),
        ),
        referenced_tables=("table_torques_01",),
        referenced_figures=("Fig. 6A-10",),
        referenced_callouts=("A", "1"),
        referenced_pages=(42,),
        is_optional=False,
        is_branching=False,
        branch_condition=None,
    )


class TestProcedureGoldenContracts:
    """Test suite for procedure contracts integrity and immutability."""

    def test_immutability_enforcement(self) -> None:
        step = _sample_procedure_step()

        with pytest.raises(ValidationError):
            # Attempt mutation
            step.sequence_number = 2  # type: ignore

        with pytest.raises(ValidationError):
            # Attempt setting extra attribute
            step.new_attr = "invalid"  # type: ignore

    def test_json_serialization_roundtrip(self) -> None:
        step = _sample_procedure_step()
        proc = AutomotiveProcedure(
            procedure_id="proc_p1_001",
            title="Cylinder Head Removal",
            description="Procedures for removing cylinder head from vehicle.",
            category=ProcedureCategory.REMOVAL_DISASSEMBLY,
            steps=(step,),
            preconditions=("Disconnect battery", "Drain coolant"),
            postconditions=("Refill coolant", "Perform leak check"),
            required_tools=step.required_tools,
            required_materials=step.required_materials,
            bound_admonitions=step.bound_admonitions,
            referenced_tables=("table_torques_01",),
            referenced_figures=("Fig. 6A-10",),
            estimated_time="1.5 hr",
            difficulty_level="Intermediate",
            page_span=(1, 1),
            bbox=BoundingBox(left=72.0, top=100.0, right=540.0, bottom=700.0),
            confidence=0.99,
            provenance=_sample_source_ref(1),
            region_ids=("reg_001", "reg_adm_01"),
            is_multi_page=False,
        )

        proc_set = AutomotiveProcedureSet(
            document_id="doc_suzuki_f8d",
            procedures=(proc,),
            total_procedures=1,
            total_steps=1,
            provenance=_sample_source_ref(1),
        )

        # Serialize
        json_str = proc_set.model_dump_json()
        assert json_str != ""

        # Roundtrip Deserialization
        loaded = AutomotiveProcedureSet.model_validate_json(json_str)
        assert loaded == proc_set
        assert loaded.procedures[0].steps[0].bound_admonitions[0].admonition_type == AdmonitionType.CAUTION
        assert loaded.procedures[0].steps[0].required_tools[0].tool_number == "09915-64510"

    def test_invalid_negative_sequence_raises(self) -> None:
        with pytest.raises(ValidationError):
            ProcedureStep(
                step_id="step_neg",
                sequence_number=0,  # ge=1 violated
                display_number="0.",
                numbering_style=StepNumberingStyle.NUMBERED,
                level=0,
                parent_step_id=None,
                child_step_ids=(),
                action_text="Invalid step",
                bbox=BoundingBox(left=0, top=0, right=10, bottom=10),
                page_number=1,
                reading_order_ref="reg",
                confidence=1.0,
                provenance=_sample_source_ref(1),
            )
