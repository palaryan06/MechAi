"""Real manual validation scenarios for diagrams."""

from mechai.contracts.diagrams import AutomotiveDiagramType
from mechai.contracts.layout import RegionType
from mechai.contracts.ordering import OrderedLayoutCIR, OrderedPageCIR
from mechai.contracts.provenance import BoundingBox, SourceRef
from mechai.diagrams.factory import DiagramEngineFactory
from tests.diagrams.test_diagram_unit import _make_region


class TestSuzukiF8DManualDiagrams:
    """Validation scenarios from Suzuki F8D Workshop Manual."""

    def test_exploded_cylinder_head_diagram(self) -> None:
        """Validate extraction of an exploded view diagram."""
        engine = DiagramEngineFactory.create_engine()
        
        regions = (
            _make_region("f1", "", RegionType.FIGURE_REGION, BoundingBox(left=50, top=100, right=500, bottom=600)),
            _make_region("c1", "Fig. 6A-1 Exploded View of Cylinder Head", RegionType.CAPTION, BoundingBox(left=50, top=610, right=500, bottom=630)),
            # Callouts
            _make_region("call1", "1", RegionType.UNKNOWN, BoundingBox(left=60, top=150, right=70, bottom=160)),
            _make_region("call2", "2", RegionType.UNKNOWN, BoundingBox(left=200, top=180, right=210, bottom=190)),
            _make_region("call3", "3", RegionType.UNKNOWN, BoundingBox(left=300, top=200, right=310, bottom=210)),
            # Labels
            _make_region("l1", "Camshaft", RegionType.UNKNOWN, BoundingBox(left=80, top=150, right=140, bottom=160)),
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
            document_id="doc_suzuki_f8d",
            total_pages=1,
            pages=(page,),
            ordered_regions=regions,
            global_graph=page.reading_order_graph,
            provenance=SourceRef(page_number=1),
        )
        
        result = engine.reconstruct_diagrams(cir)
        assert result.total_diagrams == 1
        
        diag = result.diagrams[0]
        assert diag.diagram_type == AutomotiveDiagramType.EXPLODED_VIEW
        assert diag.figure is not None
        assert diag.figure.identifier == "Fig. 6A-1"
        assert len(diag.callouts) == 3
        
        callout_texts = [c.text for c in diag.callouts]
        assert "1" in callout_texts
        assert "2" in callout_texts
        assert "3" in callout_texts
        
        assert len(diag.labels) == 1
        assert diag.labels[0].text == "Camshaft"


class TestMarutiSuzukiK10BManualDiagrams:
    """Validation scenarios from Maruti Suzuki K10B Engine Manual."""

    def test_wiring_connector_diagram(self) -> None:
        """Validate extraction of a wiring connector diagram."""
        engine = DiagramEngineFactory.create_engine()
        
        regions = (
            _make_region("f1", "", RegionType.FIGURE_REGION, BoundingBox(left=100, top=100, right=400, bottom=400)),
            # Wiring specific labels
            _make_region("l1", "Main Harness Connector", RegionType.UNKNOWN, BoundingBox(left=110, top=110, right=200, bottom=120)),
            _make_region("l2", "Ground Terminal", RegionType.UNKNOWN, BoundingBox(left=110, top=150, right=200, bottom=160)),
            _make_region("l3", "Pin 1: 5V Power", RegionType.UNKNOWN, BoundingBox(left=110, top=190, right=200, bottom=200)),
        )
        
        from mechai.contracts.layout import PageMargins
        from mechai.contracts.ordering import ReadingFlowType, ReadingOrderGraph
        
        page = OrderedPageCIR(
            page_number=2,
            width=600,
            height=800,
            margins=PageMargins(left=10, top=10, right=10, bottom=10),
            ordered_regions=regions,
            reading_order_graph=ReadingOrderGraph(nodes=tuple(), edges=tuple(), primary_path=tuple(), alternative_paths=tuple()),
            sequence_confidence=1.0,
            reading_flow_type=ReadingFlowType.SINGLE_COLUMN,
        )
        
        cir = OrderedLayoutCIR(
            document_id="doc_k10b",
            total_pages=1,
            pages=(page,),
            ordered_regions=regions,
            global_graph=page.reading_order_graph,
            provenance=SourceRef(page_number=2),
        )
        
        result = engine.reconstruct_diagrams(cir)
        assert result.total_diagrams == 1
        
        diag = result.diagrams[0]
        # Classified as wiring diagram because of keywords in labels
        assert diag.diagram_type == AutomotiveDiagramType.WIRING_DIAGRAM
        assert len(diag.labels) == 3
