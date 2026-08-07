"""Unit tests for Automotive Procedure Intelligence Engine (RFC-AUTO-002)."""

from __future__ import annotations

import pytest

from mechai.contracts.layout import BoundingBox, ExtractionMethod, RegionType, SourceRef
from mechai.contracts.ordering import OrderedLayoutRegion
from mechai.contracts.procedures import (
    AdmonitionType,
    ProcedureCategory,
    StepNumberingStyle,
)
from mechai.procedures.admonition_binder import AdmonitionBinder
from mechai.procedures.boundary_detector import BoundaryDetector
from mechai.procedures.config import ProcedureEngineConfig
from mechai.procedures.cross_ref_resolver import CrossReferenceResolver
from mechai.procedures.factory import AutomotiveProcedureEngineFactory
from mechai.procedures.requirement_extractor import RequirementExtractor
from mechai.procedures.step_parser import StepParser


def _make_region(
    reg_id: str,
    text: str,
    reg_type: RegionType,
    page_number: int = 1,
) -> OrderedLayoutRegion:
    """Helper to assemble an OrderedLayoutRegion for testing."""
    return OrderedLayoutRegion(
        id=reg_id,
        bbox=BoundingBox(left=50.0, top=50.0, right=500.0, bottom=100.0),
        page_number=page_number,
        region_type=reg_type,
        confidence=0.98,
        provenance=SourceRef(
            page_number=page_number,
            bbox=BoundingBox(left=50.0, top=50.0, right=500.0, bottom=100.0),
            extraction_method=ExtractionMethod.RULE,
            confidence=0.98,
        ),
        text=text,
        reading_order_index=1,
        reading_depth=0,
        is_primary_flow=True,
    )


class TestStepParser:
    """Test suite for StepParser numbering styles and conditions."""

    def test_parse_numbered_steps(self) -> None:
        parser = StepParser()
        text = (
            "1. Disconnect negative cable from battery.\n"
            "2. Drain engine cooling system.\n"
            "3. Remove air cleaner assembly (if equipped)."
        )
        steps = parser.parse_text_lines(text)
        assert len(steps) == 3
        assert steps[0].display_number == "1."
        assert steps[0].action_text == "Disconnect negative cable from battery."
        assert steps[0].numbering_style == StepNumberingStyle.NUMBERED
        assert steps[0].is_optional is False

        assert steps[2].display_number == "3."
        assert steps[2].is_optional is True

    def test_parse_alphabetical_substeps(self) -> None:
        parser = StepParser()
        text = (
            "a) Loosen cylinder head bolts.\n"
            "b) Remove camshaft bearing caps.\n"
            "c) Take out intake and exhaust camshafts."
        )
        steps = parser.parse_text_lines(text)
        assert len(steps) == 3
        assert steps[0].display_number == "a)"
        assert steps[0].numbering_style == StepNumberingStyle.ALPHABETICAL
        assert steps[0].indent_level == 1

    def test_parse_roman_numerals(self) -> None:
        parser = StepParser()
        text = (
            "(i) Inspect valve stem for wear.\n"
            "(ii) Measure valve stem-to-guide clearance."
        )
        steps = parser.parse_text_lines(text)
        assert len(steps) == 2
        assert steps[0].display_number == "(i)"
        assert steps[0].numbering_style == StepNumberingStyle.ROMAN
        assert steps[0].indent_level == 2

    def test_parse_bullet_steps(self) -> None:
        parser = StepParser()
        text = (
            "• Clean mating surfaces of cylinder block.\n"
            "• Apply fresh oil to all bearing surfaces."
        )
        steps = parser.parse_text_lines(text)
        assert len(steps) == 2
        assert steps[0].display_number == "•"
        assert steps[0].numbering_style == StepNumberingStyle.BULLET

    def test_branching_condition_detection(self) -> None:
        parser = StepParser()
        text = "4. If valve clearance is out of specification, go to step 8 for shim adjustment."
        steps = parser.parse_text_lines(text)
        assert len(steps) == 1
        assert steps[0].is_branching is True
        assert steps[0].branch_condition is not None
        assert "go to step" in steps[0].branch_condition.lower()


class TestRequirementExtractor:
    """Test suite for tool, SST, and material extraction."""

    def test_sst_extraction(self) -> None:
        extractor = RequirementExtractor()
        text = (
            "Compress valve spring using SST 09916-14510 (Valve spring compressor) "
            "and remove valve cotters using special tool 09916-84511."
        )
        tools = extractor.extract_tools(text)
        assert len(tools) == 2
        assert tools[0].is_sst is True
        assert tools[0].tool_number == "09916-14510"
        assert "Valve spring compressor" in tools[0].name
        assert tools[1].is_sst is True
        assert tools[1].tool_number == "09916-84511"

    def test_standard_tool_extraction(self) -> None:
        extractor = RequirementExtractor()
        text = "Tighten cylinder head bolts using a torque wrench. Measure clearance with a feeler gauge."
        tools = extractor.extract_tools(text)
        tool_names = [t.name.lower() for t in tools]
        assert "torque wrench" in tool_names
        assert "feeler gauge" in tool_names

    def test_materials_and_mandatory_replacements(self) -> None:
        extractor = RequirementExtractor()
        text = (
            "Apply Suzuki Bond 1215 to cylinder head mating surface. "
            "Always replace with new gasket and new cotter pin upon reassembly."
        )
        mats = extractor.extract_materials(text)
        mat_names = [m.name.lower() for m in mats]
        assert any("suzuki bond" in n for n in mat_names)
        assert any("gasket" in n for n in mat_names)
        assert any("cotter pin" in n for n in mat_names)

        # Verify replacement flags
        repl_flags = [m.is_replacement_mandatory for m in mats if "gasket" in m.name.lower()]
        assert any(repl_flags)


class TestAdmonitionBinder:
    """Test suite for safety warnings and technical notes."""

    def test_classify_admonition_regions(self) -> None:
        binder = AdmonitionBinder()
        warn_reg = _make_region("reg_w1", "WARNING: High voltage circuit. Disconnect service plug.", RegionType.WARNING_BOX)
        caution_reg = _make_region("reg_c1", "CAUTION: Do not scratch machined aluminum surface.", RegionType.WARNING_BOX)
        note_reg = _make_region("reg_n1", "NOTE: Mark timing chain links before removal.", RegionType.NOTE_BOX)

        w_adms = binder.extract_admonitions_from_region(warn_reg)
        assert len(w_adms) == 1
        assert w_adms[0].admonition_type == AdmonitionType.WARNING

        c_adms = binder.extract_admonitions_from_region(caution_reg)
        assert len(c_adms) == 1
        assert c_adms[0].admonition_type == AdmonitionType.CAUTION

        n_adms = binder.extract_admonitions_from_region(note_reg)
        assert len(n_adms) == 1
        assert n_adms[0].admonition_type == AdmonitionType.NOTE


class TestBoundaryDetector:
    """Test suite for boundary detection and category classification."""

    def test_procedure_heading_detection(self) -> None:
        detector = BoundaryDetector()
        h1 = _make_region("h1", "Cylinder Head Removal", RegionType.HEADING)
        h2 = _make_region("h2", "Timing Belt Inspection & Adjustment", RegionType.HEADING)
        h3 = _make_region("h3", "General System Description", RegionType.HEADING)

        assert detector.is_procedure_heading(h1) is True
        assert detector.is_procedure_heading(h2) is True
        assert detector.is_procedure_heading(h3) is False

    def test_category_classification(self) -> None:
        detector = BoundaryDetector()
        assert detector.classify_category("Engine Assembly Disassembly") == ProcedureCategory.REMOVAL_DISASSEMBLY
        assert detector.classify_category("Water Pump Installation") == ProcedureCategory.INSTALLATION_REASSEMBLY
        assert detector.classify_category("Valve Lash Inspection") == ProcedureCategory.INSPECTION_ADJUSTMENT
        assert detector.classify_category("Periodic Maintenance Schedule") == ProcedureCategory.MAINTENANCE
        assert detector.classify_category("Complete Engine Overhaul") == ProcedureCategory.OVERHAUL

    def test_preconditions_and_postconditions(self) -> None:
        detector = BoundaryDetector()
        text = (
            "Preparation:\n"
            "Disconnect negative battery cable.\n"
            "Drain coolant completely.\n"
            "1. Remove cylinder head cover.\n"
            "After installation:\n"
            "Refill coolant and check for leaks."
        )
        pre = detector.extract_preconditions(text)
        post = detector.extract_postconditions(text)
        assert len(pre) >= 2
        assert len(post) >= 1


class TestCrossReferenceResolver:
    """Test suite for cross-reference extraction."""

    def test_cross_refs(self) -> None:
        resolver = CrossReferenceResolver()
        text = (
            "Refer to Table 6A-1 for torque values. Align timing marks as shown in Fig. 6A-12. "
            "Loosen bolt [A] and remove pin (1). See page 45."
        )
        tables, figs, callouts, pages = resolver.resolve_references(text)
        assert len(tables) >= 1
        assert "Fig. 6A-12" in figs
        assert "A" in callouts or "1" in callouts
        assert 45 in pages


class TestProcedureEngineFactory:
    """Test suite for factory creation."""

    def test_factory_creates_engine(self) -> None:
        engine = AutomotiveProcedureEngineFactory.create()
        assert engine is not None

    def test_factory_with_custom_config(self) -> None:
        config = ProcedureEngineConfig(min_confidence=0.85)
        engine = AutomotiveProcedureEngineFactory.create(config)
        assert engine is not None
