"""Golden dataset tests for specifications to prevent regression."""

import pytest

from mechai.specifications.factory import SpecificationEngineFactory
from mechai.contracts.ordering import OrderedLayoutCIR, ReadingOrderGraph
from mechai.contracts.procedures import AutomotiveProcedureSet, AutomotiveProcedure, ProcedureStep, StepNumberingStyle
from mechai.contracts.provenance import SourceRef, BoundingBox
from mechai.contracts.specifications import SpecificationType


class TestSpecificationGolden:
    """Golden tests for ensuring the engine does not regress on critical facts."""

    @pytest.fixture
    def engine(self):
        return SpecificationEngineFactory.create_engine()

    def test_golden_dataset(self, engine) -> None:
        """Run through a predefined set of tricky strings."""
        test_cases = [
            ("Tighten to 45 N.m + 90°", 45.0, "N.m", 90.0, SpecificationType.TORQUE),
            ("Tighten bolt to 25 ft-lb", 25.0, "ft-lb", None, SpecificationType.TORQUE),
            ("Apply thread lock and tighten to 30 N.m", 30.0, "N.m", None, SpecificationType.TORQUE),
            ("Clearance: 0.15 - 0.20 mm", None, "mm", None, SpecificationType.CLEARANCE),
        ]
        
        from mechai.contracts.ordering import ReadingOrderGraph
        cir = OrderedLayoutCIR(document_id="golden", total_pages=1, global_graph=ReadingOrderGraph(), pages=())
        ref = SourceRef(page_number=1)
        bbox = BoundingBox(left=0, top=0, right=100, bottom=100)
        
        steps = [
            ProcedureStep(
                step_id=f"s{i}",
                sequence_number=i + 1,
                display_number=str(i + 1),
                numbering_style=StepNumberingStyle.NUMBERED,
                level=0,
                action_text=case[0],
                bbox=bbox,
                page_number=1,
                reading_order_ref=f"r{i}",
                provenance=ref
            )
            for i, case in enumerate(test_cases)
        ]
        
        proc = AutomotiveProcedure(
            procedure_id="p1", title="Golden Test Procedure", steps=tuple(steps), page_span=(1, 1), provenance=ref
        )
        proc_set = AutomotiveProcedureSet(document_id="golden", procedures=(proc,), total_procedures=1, total_steps=4, provenance=ref)
        
        result = engine.extract_specifications(cir, procedures=proc_set)
        
        # We expect 3 torques and 1 specification
        assert len(result.torques) == 3
        assert len(result.specifications) == 1
        
        tqs = result.torques
        sps = result.specifications
        
        # Case 0
        assert tqs[0].value.numeric_value == 45.0
        assert tqs[0].value.original_unit == "N.m"
        assert tqs[0].tightening_angle_degrees == 90.0
        
        # Case 1
        assert tqs[1].value.numeric_value == 25.0
        assert tqs[1].value.original_unit == "ft-lb"
        
        # Case 2
        assert tqs[2].value.numeric_value == 30.0
        assert tqs[2].value.original_unit == "N.m"
        
        # Case 3
        assert sps[0].value.tolerance_min == 0.15
        assert sps[0].value.tolerance_max == 0.20
        assert sps[0].value.original_unit == "mm"
