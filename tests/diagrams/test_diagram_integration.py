"""Integration tests for diagram engine."""

from mechai.contracts.layout import RegionType
from mechai.contracts.ordering import OrderedLayoutCIR, OrderedPageCIR
from mechai.contracts.provenance import BoundingBox, SourceRef
from mechai.diagrams.factory import DiagramEngineFactory
from tests.diagrams.test_diagram_unit import _make_region


class TestDiagramEngineIntegration:
    """Integration pipeline tests for diagram engine."""

    def test_pipeline_integration(self) -> None:
        """Test processing a complete OrderedLayoutCIR into an AutomotiveDiagramSet."""
        engine = DiagramEngineFactory.create_engine()
        
        # Mock CIR with one figure and one callout
        regions = (
            _make_region("f1", "", RegionType.FIGURE_REGION, BoundingBox(left=10, top=10, right=200, bottom=200)),
            _make_region("c1", "Fig. 1 Exploded View", RegionType.CAPTION, BoundingBox(left=10, top=205, right=200, bottom=220)),
            _make_region("call1", "1", RegionType.UNKNOWN, BoundingBox(left=20, top=20, right=30, bottom=30)),
            _make_region("l1", "Bolt", RegionType.UNKNOWN, BoundingBox(left=35, top=20, right=60, bottom=30)),
        )
        
        from mechai.contracts.layout import PageMargins
        from mechai.contracts.ordering import ReadingFlowType, ReadingOrderGraph
        
        page = OrderedPageCIR(
            page_number=1,
            width=600,
            height=800,
            margins=PageMargins(left=10, top=10, right=10, bottom=10),
            ordered_regions=regions,
            reading_order_graph=ReadingOrderGraph(nodes=tuple(), edges=tuple(), primary_path=tuple(), alternative_paths=tuple()),
            sequence_confidence=1.0,
            reading_flow_type=ReadingFlowType.SINGLE_COLUMN,
        )
        
        cir = OrderedLayoutCIR(
            document_id="doc1",
            total_pages=1,
            pages=(page,),
            ordered_regions=regions,
            global_graph=page.reading_order_graph,
            provenance=SourceRef(page_number=1),
        )
        
        result = engine.reconstruct_diagrams(cir)
        
        assert result.total_diagrams == 1
        diag = result.diagrams[0]
        
        assert diag.figure is not None
        assert diag.figure.identifier == "Fig. 1"
        assert len(diag.callouts) == 1
        assert diag.callouts[0].text == "1"
        assert len(diag.labels) == 1
        assert diag.labels[0].text == "Bolt"
        assert len(diag.relationships) == 1
        assert diag.relationships[0].source_id == diag.callouts[0].callout_id
        assert diag.relationships[0].target_id == diag.labels[0].label_id
