"""Tests against actual text excerpts from the Suzuki F8D and K10B manuals."""

import pytest

from mechai.specifications.factory import SpecificationEngineFactory
from mechai.contracts.ordering import OrderedLayoutCIR, ReadingOrderGraph
from mechai.contracts.procedures import AutomotiveProcedureSet, AutomotiveProcedure, ProcedureStep, StepNumberingStyle
from mechai.contracts.provenance import SourceRef, BoundingBox


class TestRealManualSnippets:
    """Validate engine against excerpts from real manuals."""

    @pytest.fixture
    def engine(self):
        return SpecificationEngineFactory.create_engine()

    def test_suzuki_f8d_cylinder_head(self, engine) -> None:
        """Test F8D cylinder head torque sequence."""
        from mechai.contracts.ordering import ReadingOrderGraph
        cir = OrderedLayoutCIR(document_id="f8d", total_pages=1, global_graph=ReadingOrderGraph(), pages=())
        ref = SourceRef(page_number=35)
        bbox = BoundingBox(left=0, top=0, right=100, bottom=100)
        
        proc = AutomotiveProcedure(
            procedure_id="p1",
            title="Cylinder Head F8D",
            steps=(
                ProcedureStep(
                    step_id="s1",
                    sequence_number=1,
                    display_number="1",
                    numbering_style=StepNumberingStyle.NUMBERED,
                    level=0,
                    action_text="Tighten cylinder head bolts to 4.5 kgf-m.",
                    bbox=bbox,
                    page_number=1,
                    reading_order_ref="r1",
                    provenance=ref
                ),
            ),
            page_span=(35, 35),
            provenance=ref
        )
        proc_set = AutomotiveProcedureSet(document_id="f8d", procedures=(proc,), total_procedures=1, total_steps=1, provenance=ref)
        
        result = engine.extract_specifications(cir, procedures=proc_set)
        
        assert len(result.torques) == 1
        tq = result.torques[0]
        assert tq.target_component == "cylinder head bolts"
        assert tq.value.raw_value == "4.5 kgf-m"
        assert abs(tq.value.canonical_value - 44.13) < 0.1  # type: ignore

    def test_suzuki_k10b_valve_clearance(self, engine) -> None:
        """Test K10B valve clearance (cold)."""
        from mechai.contracts.ordering import ReadingOrderGraph
        cir = OrderedLayoutCIR(document_id="k10b", total_pages=1, global_graph=ReadingOrderGraph(), pages=())
        ref = SourceRef(page_number=120)
        bbox = BoundingBox(left=0, top=0, right=100, bottom=100)
        
        proc = AutomotiveProcedure(
            procedure_id="p1",
            title="Valve Clearance Inspection K10B",
            steps=(
                ProcedureStep(
                    step_id="s1",
                    sequence_number=1,
                    display_number="1",
                    numbering_style=StepNumberingStyle.NUMBERED,
                    level=0,
                    action_text="Valve clearance (when cold): IN: 0.13 - 0.17 mm",
                    bbox=bbox,
                    page_number=1,
                    reading_order_ref="r1",
                    provenance=ref
                ),
            ),
            page_span=(120, 120),
            provenance=ref
        )
        proc_set = AutomotiveProcedureSet(document_id="k10b", procedures=(proc,), total_procedures=1, total_steps=1, provenance=ref)
        
        result = engine.extract_specifications(cir, procedures=proc_set)
        
        assert len(result.specifications) == 1
        sp = result.specifications[0]
        assert sp.value.tolerance_min == 0.13
        assert sp.value.tolerance_max == 0.17
        assert sp.measurement_condition == "when cold"
        assert sp.applicability.engine_code == "K10B"
