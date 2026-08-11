"""Unit tests for diagram engine components."""

from mechai.contracts.diagrams import AutomotiveDiagramType
from mechai.contracts.layout import RegionType
from mechai.contracts.ordering import OrderedLayoutRegion
from mechai.contracts.procedures import AutomotiveProcedure, AutomotiveProcedureSet
from mechai.contracts.provenance import BoundingBox, SourceRef
from mechai.contracts.tables import AutomotiveTable, AutomotiveTableSet, AutomotiveTableType
from mechai.diagrams.callout_detector import CalloutDetector
from mechai.diagrams.classifier import DiagramClassifier
from mechai.diagrams.diagram_detector import DiagramDetector
from mechai.diagrams.procedure_linker import ProcedureLinker
from mechai.diagrams.table_linker import TableLinker


def _make_region(
    region_id: str,
    text: str,
    region_type: RegionType,
    bbox: BoundingBox,
) -> OrderedLayoutRegion:
    return OrderedLayoutRegion(
        id=region_id,
        bbox=bbox,
        page_number=1,
        region_type=region_type,
        confidence=1.0,
        provenance=SourceRef(page_number=1),
        text=text,
        reading_order_index=1,
    )


class TestDiagramDetector:
    def test_group_diagrams(self) -> None:
        detector = DiagramDetector()
        regions = [
            _make_region("f1", "", RegionType.FIGURE_REGION, BoundingBox(left=10, top=10, right=200, bottom=200)),
            _make_region("c1", "Fig. 1 Test", RegionType.CAPTION, BoundingBox(left=10, top=205, right=200, bottom=220)),
            _make_region("call1", "1", RegionType.UNKNOWN, BoundingBox(left=20, top=20, right=30, bottom=30)),
        ]
        
        groups = detector.detect_diagrams(regions)
        assert len(groups) == 1
        assert groups[0]["figure_region"].id == "f1"
        assert groups[0]["caption_region"].id == "c1"
        assert len(groups[0]["content_regions"]) == 1
        assert groups[0]["content_regions"][0].id == "call1"

    def test_extract_figure(self) -> None:
        detector = DiagramDetector()
        caption = _make_region("c1", "Fig. 2 Exploded View", RegionType.CAPTION, BoundingBox(left=0, top=0, right=0, bottom=0))
        fig = detector.extract_figure(caption)
        assert fig is not None
        assert fig.identifier == "Fig. 2"


class TestCalloutDetector:
    def test_detect_numeric_callout(self) -> None:
        detector = CalloutDetector()
        reg = _make_region("r1", "12", RegionType.UNKNOWN, BoundingBox(left=0, top=0, right=0, bottom=0))
        callouts = detector.detect_callouts(reg)
        assert len(callouts) == 1
        assert callouts[0].text == "12"

    def test_detect_bracket_callout(self) -> None:
        detector = CalloutDetector()
        reg = _make_region("r1", "[A]", RegionType.UNKNOWN, BoundingBox(left=0, top=0, right=0, bottom=0))
        callouts = detector.detect_callouts(reg)
        assert len(callouts) == 1
        assert callouts[0].text == "[A]"


class TestDiagramClassifier:
    def test_classify_exploded_view_from_title(self) -> None:
        classifier = DiagramClassifier()
        detector = DiagramDetector()
        caption = _make_region("c1", "Fig. 1 Exploded View of Engine", RegionType.CAPTION, BoundingBox(left=0, top=0, right=0, bottom=0))
        fig = detector.extract_figure(caption)
        
        dtype = classifier.classify(fig, tuple(), tuple())
        assert dtype == AutomotiveDiagramType.EXPLODED_VIEW

    def test_classify_wiring_diagram_from_labels(self) -> None:
        classifier = DiagramClassifier()
        from mechai.contracts.diagrams import DiagramLabel
        labels = (
            DiagramLabel(label_id="l1", text="Main Harness", bbox=BoundingBox(left=0, top=0, right=0, bottom=0), provenance=SourceRef(page_number=1)),
            DiagramLabel(label_id="l2", text="Ground", bbox=BoundingBox(left=0, top=0, right=0, bottom=0), provenance=SourceRef(page_number=1)),
        )
        dtype = classifier.classify(None, labels, tuple())
        assert dtype == AutomotiveDiagramType.WIRING_DIAGRAM


class TestLinkers:
    def test_table_linker(self) -> None:
        linker = TableLinker()
        from mechai.contracts.diagrams import DiagramFigure
        fig = DiagramFigure(figure_id="f1", title="Refer to Table 1", identifier="Fig. 1", bbox=BoundingBox(left=0, top=0, right=0, bottom=0), provenance=SourceRef(page_number=1))
        
        from mechai.contracts.tables import AutomotiveTableHeader
        table = AutomotiveTable(table_id="t1", table_type=AutomotiveTableType.GENERAL_SPECIFICATION, title="Table 1 Specs", header=AutomotiveTableHeader(depth=1), rows=tuple(), page_number=1, page_span=(1,1), bbox=BoundingBox(left=0, top=0, right=0, bottom=0), provenance=SourceRef(page_number=1), is_multi_page=False)
        tset = AutomotiveTableSet(document_id="doc1", tables=(table,), total_tables=1, provenance=SourceRef(page_number=1))
        
        linked = linker.link_tables(fig, tuple(), tset)
        assert "t1" in linked

    def test_procedure_linker(self) -> None:
        linker = ProcedureLinker()
        from mechai.contracts.diagrams import DiagramFigure
        fig = DiagramFigure(figure_id="f1", title="Fig. 1A", identifier="Fig. 1A", bbox=BoundingBox(left=0, top=0, right=0, bottom=0), provenance=SourceRef(page_number=1))
        
        from mechai.contracts.procedures import ProcedureCategory
        proc = AutomotiveProcedure(procedure_id="p1", title="Test Proc", category=ProcedureCategory.GENERAL_PROCEDURE, steps=tuple(), preconditions=tuple(), postconditions=tuple(), required_tools=tuple(), required_materials=tuple(), bound_admonitions=tuple(), referenced_tables=tuple(), referenced_figures=("Fig. 1A",), estimated_time=None, difficulty_level=None, page_span=(1,1), bbox=BoundingBox(left=0, top=0, right=0, bottom=0), confidence=1.0, provenance=SourceRef(page_number=1), region_ids=tuple(), is_multi_page=False)
        pset = AutomotiveProcedureSet(document_id="doc1", procedures=(proc,), total_procedures=1, total_steps=0, provenance=SourceRef(page_number=1))
        
        linked = linker.link_procedures(fig, pset)
        assert "p1" in linked
