"""Integration tests for the Automotive Specification Engine."""

import pytest

from mechai.specifications.factory import SpecificationEngineFactory
from mechai.contracts.ordering import OrderedLayoutCIR, ReadingOrderGraph
from mechai.contracts.procedures import AutomotiveProcedureSet, AutomotiveProcedure, ProcedureStep, StepNumberingStyle
from mechai.contracts.tables import AutomotiveTableSet, AutomotiveTable, AutomotiveTableRow, AutomotiveTableCell
from mechai.contracts.provenance import SourceRef, ExtractionMethod, BoundingBox


class TestSpecificationIntegration:
    """End-to-end extraction from structured inputs."""

    @pytest.fixture
    def engine(self):
        return SpecificationEngineFactory.create_engine()

    def test_extract_from_procedure(self, engine) -> None:
        """Test extraction from a procedure."""
        from mechai.contracts.ordering import ReadingOrderGraph
        cir = OrderedLayoutCIR(document_id="doc1", total_pages=1, global_graph=ReadingOrderGraph(), pages=())
        ref = SourceRef(page_number=1)
        bbox = BoundingBox(left=0, top=0, right=100, bottom=100)
        
        proc = AutomotiveProcedure(
            procedure_id="p1",
            title="Cylinder Head Installation for K10B",
            steps=(
                ProcedureStep(
                    step_id="s1",
                    sequence_number=1,
                    display_number="1",
                    numbering_style=StepNumberingStyle.NUMBERED,
                    level=0,
                    action_text="Tighten cylinder head bolts to 45 N.m.",
                    bbox=bbox,
                    page_number=1,
                    reading_order_ref="r1",
                    provenance=ref
                ),
            ),
            page_span=(1, 1),
            provenance=ref
        )
        proc_set = AutomotiveProcedureSet(document_id="doc1", procedures=(proc,), total_procedures=1, total_steps=1, provenance=ref)
        
        result = engine.extract_specifications(cir, procedures=proc_set)
        
        assert len(result.torques) == 1
        tq = result.torques[0]
        assert tq.value.numeric_value == 45.0
        # Inherited applicability from title
        assert tq.applicability.engine_code == "K10B"

    def test_extract_from_table(self, engine) -> None:
        """Test extraction from a table."""
        from mechai.contracts.ordering import ReadingOrderGraph
        cir = OrderedLayoutCIR(document_id="doc1", total_pages=1, global_graph=ReadingOrderGraph(), pages=())
        ref = SourceRef(page_number=1)
        bbox = BoundingBox(left=0, top=0, right=100, bottom=100)
        
        from mechai.contracts.tables import AutomotiveTableHeader
        table = AutomotiveTable(
            table_id="tb1",
            page_number=1,
            bbox=bbox,
            header=AutomotiveTableHeader(),
            title="Torque Specifications (M/T)",
            rows=(
                AutomotiveTableRow(
                    row_index=0,
                    cells=(
                        AutomotiveTableCell(
                            cell_id="c1", row_index=0, col_index=0, raw_text="Flywheel bolt",
                            bbox=bbox, page_number=1, reading_order_ref="r1", provenance=ref
                        ),
                        AutomotiveTableCell(
                            cell_id="c2", row_index=0, col_index=1, raw_text="70 N.m",
                            bbox=bbox, page_number=1, reading_order_ref="r2", provenance=ref
                        ),
                    )
                ),
            ),
            provenance=ref
        )
        table_set = AutomotiveTableSet(document_id="doc1", tables=(table,), provenance=ref)
        
        result = engine.extract_specifications(cir, tables=table_set)
        
        assert len(result.torques) == 1
        tq = result.torques[0]
        assert tq.value.numeric_value == 70.0
        assert tq.target_component == "Flywheel bolt"
        assert tq.applicability.transmission == "M/T"
