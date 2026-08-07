"""Unit tests for Automotive Table Intelligence Engine (RFC-AUTO-001).

Tests grid reconstruction, multi-column alignment, header depth resolution,
unit normalization, footnote association, table classification, and continuation stitching.
"""

from __future__ import annotations

import pytest

from mechai.contracts.layout import RegionType
from mechai.contracts.ordering import OrderedLayoutRegion
from mechai.contracts.provenance import BoundingBox, ExtractionMethod, SourceRef
from mechai.contracts.tables import (
    AutomotiveTableCell,
    AutomotiveTableHeader,
    AutomotiveTableRow,
    AutomotiveTableType,
    CellAlignment,
    CellType,
)
from mechai.tables import (
    AutomotiveFootnoteExtractor,
    AutomotiveTableClassifier,
    AutomotiveTableContinuationStitcher,
    AutomotiveTableEngine,
    AutomotiveTableEngineFactory,
    AutomotiveUnitExtractor,
    SpatialGridReconstructor,
    TableEngineConfig,
)


def _make_table_region(
    region_id: str,
    text: str,
    page_number: int = 1,
    bbox: BoundingBox | None = None,
) -> OrderedLayoutRegion:
    b = bbox or BoundingBox(left=50.0, top=100.0, right=550.0, bottom=300.0)
    return OrderedLayoutRegion(
        id=region_id,
        bbox=b,
        page_number=page_number,
        region_type=RegionType.TABLE_REGION,
        confidence=0.95,
        provenance=SourceRef(
            page_number=page_number,
            bbox=b,
            extraction_method=ExtractionMethod.RULE,
            confidence=0.95,
        ),
        text=text,
        reading_order_index=1,
        reading_depth=0,
        is_primary_flow=True,
    )


class TestAutomotiveUnitExtractor:
    """Test suite for automotive unit extraction and normalization."""

    def test_torque_units(self) -> None:
        assert AutomotiveUnitExtractor.extract_unit_from_header("Cylinder Head Bolt Torque (N·m)") == "N·m"
        assert AutomotiveUnitExtractor.extract_unit_from_header("Torque [ft-lb]") == "ft-lb"
        assert AutomotiveUnitExtractor.extract_unit_from_header("Tightening Torque (kgf-m)") == "kgf-m"
        assert AutomotiveUnitExtractor.extract_unit_from_header("Fastener Torque N.m") == "N·m"

    def test_clearance_and_pressure_units(self) -> None:
        assert AutomotiveUnitExtractor.extract_unit_from_header("Valve Clearance (mm)") == "mm"
        assert AutomotiveUnitExtractor.extract_unit_from_header("Oil Pressure [kPa]") == "kPa"
        assert AutomotiveUnitExtractor.extract_unit_from_header("Tire Pressure (psi)") == "psi"
        assert AutomotiveUnitExtractor.extract_unit_from_header("Bore Diameter (in)") == "in"

    def test_fluid_and_electrical_units(self) -> None:
        assert AutomotiveUnitExtractor.extract_unit_from_header("Engine Oil Capacity (L)") == "L"
        assert AutomotiveUnitExtractor.extract_unit_from_header("Coolant Volume (qt)") == "qt"
        assert AutomotiveUnitExtractor.extract_unit_from_header("Sensor Resistance (kΩ)") == "kΩ"
        assert AutomotiveUnitExtractor.extract_unit_from_header("Battery Voltage (V)") == "V"

    def test_extract_unit_from_value(self) -> None:
        val, unit = AutomotiveUnitExtractor.extract_unit_from_value("25.0 N·m")
        assert val == "25.0"
        assert unit == "N·m"

        val, unit = AutomotiveUnitExtractor.extract_unit_from_value("0.025 - 0.045 mm")
        assert val == "0.025 - 0.045"
        assert unit == "mm"

    def test_is_unit_row(self) -> None:
        assert AutomotiveUnitExtractor.is_unit_row(["mm", "mm", "N·m"]) is True
        assert AutomotiveUnitExtractor.is_unit_row(["Item", "Standard", "Limit"]) is False


class TestAutomotiveFootnoteExtractor:
    """Test suite for footnote marker and definition extraction."""

    def test_cell_markers_extraction(self) -> None:
        assert AutomotiveFootnoteExtractor.extract_cell_markers("Cylinder Head Bolt *1") == ("*1",)
        assert AutomotiveFootnoteExtractor.extract_cell_markers("Connecting Rod (a) [1]") == ("(a)", "[1]")
        assert AutomotiveFootnoteExtractor.extract_cell_markers("Standard Value") == ()

    def test_parse_footnote_lines(self) -> None:
        lines = [
            "*1: Replace bolt with new part upon reassembly.",
            "(a) Apply clean engine oil to threads.",
            "* Apply liquid gasket.",
        ]
        prov = SourceRef(page_number=1, extraction_method=ExtractionMethod.RULE, confidence=1.0)
        footnotes = AutomotiveFootnoteExtractor.parse_footnote_lines(lines, page_number=1, provenance=prov)
        assert len(footnotes) == 3
        assert footnotes[0].marker == "*1"
        assert "Replace bolt" in footnotes[0].text
        assert footnotes[1].marker == "(a)"
        assert footnotes[2].marker == "*"


class TestAutomotiveTableClassifier:
    """Test suite for 10-category deterministic table classification."""

    def test_classify_torque(self) -> None:
        t_type = AutomotiveTableClassifier.classify(
            title="Tightening Torque Specifications",
            header_names=["Fastener", "Thread Size", "Torque (N·m)"],
            sample_cells=["Cylinder Head Bolt", "M10", "55.0 N·m"],
        )
        assert t_type == AutomotiveTableType.TORQUE_SPECIFICATION

    def test_classify_service_interval(self) -> None:
        t_type = AutomotiveTableClassifier.classify(
            title="Periodic Maintenance Schedule",
            header_names=["Interval (Months)", "km x 1000", "Engine Oil", "Air Cleaner"],
            sample_cells=["12", "15", "Replace", "Inspect"],
        )
        assert t_type == AutomotiveTableType.SERVICE_INTERVAL

    def test_classify_wear_limit(self) -> None:
        t_type = AutomotiveTableClassifier.classify(
            title="Piston and Cylinder Wear Limits",
            header_names=["Item", "Standard (mm)", "Wear Limit (mm)"],
            sample_cells=["Piston Diameter", "68.45", "68.30"],
        )
        assert t_type == AutomotiveTableType.WEAR_LIMIT

    def test_classify_bearing_clearance(self) -> None:
        t_type = AutomotiveTableClassifier.classify(
            title="Crankshaft Main Bearing Selection",
            header_names=["Journal Color Code", "Crankcase Grade", "Bearing Thickness Code"],
            sample_cells=["Green", "1", "Black"],
        )
        assert t_type == AutomotiveTableType.BEARING_CLEARANCE

    def test_classify_fluid_capacity(self) -> None:
        t_type = AutomotiveTableClassifier.classify(
            title="Fluid Capacities and Lubricants",
            header_names=["System", "Capacity (L)", "Recommended Fluid"],
            sample_cells=["Engine Oil (Dry Fill)", "3.5", "5W-30 API SP"],
        )
        assert t_type == AutomotiveTableType.FLUID_CAPACITY

    def test_classify_electrical(self) -> None:
        t_type = AutomotiveTableClassifier.classify(
            title="Sensor Resistance Standards",
            header_names=["Sensor Terminal", "Condition", "Standard Resistance (kΩ)"],
            sample_cells=["ECT Sensor 1-2", "20 °C", "2.2 - 2.7"],
        )
        assert t_type == AutomotiveTableType.ELECTRICAL_SPECIFICATION

    def test_classify_diagnostic(self) -> None:
        t_type = AutomotiveTableClassifier.classify(
            title="Diagnostic Trouble Code Table",
            header_names=["DTC Code", "Symptom", "Probable Cause"],
            sample_cells=["P0300", "Random Misfire", "Spark Plug Fault"],
        )
        assert t_type == AutomotiveTableType.DIAGNOSTIC_LOOKUP

    def test_classify_tightening_sequence(self) -> None:
        t_type = AutomotiveTableClassifier.classify(
            title="Cylinder Head Bolt Tightening Sequence",
            header_names=["Step", "Torque Order", "Angle Turn"],
            sample_cells=["Step 1", "1 to 8", "90 degrees"],
        )
        assert t_type == AutomotiveTableType.TIGHTENING_SEQUENCE


class TestSpatialGridReconstructor:
    """Test suite for 2D spatial grid reconstruction."""

    def test_pipe_delimited_table_reconstruction(self) -> None:
        table_text = (
            "| Fastener | Thread | Torque (N·m) |\n"
            "| --- | --- | --- |\n"
            "| Cylinder Head Bolt | M10 | 55.0 |\n"
            "| Camshaft Sprocket Bolt | M8 | 22.0 |\n"
        )
        region = _make_table_region("tbl_reg_01", table_text)
        reconstructor = SpatialGridReconstructor()
        header, rows, num_rows, num_cols = reconstructor.reconstruct_grid(region)

        assert num_cols == 3
        assert num_rows == 2
        assert header.flat_column_names == ("Fastener", "Thread", "Torque (N·m)")
        assert header.column_units.get(2) == "N·m"
        assert rows[0].cells[0].raw_text == "Cylinder Head Bolt"
        assert rows[0].cells[2].alignment == CellAlignment.RIGHT

    def test_whitespace_aligned_table_reconstruction(self) -> None:
        table_text = (
            "Item                  Standard (mm)    Limit (mm)\n"
            "Piston Clearance      0.020 - 0.040    0.070\n"
            "Piston Ring Gap       0.15 - 0.30      0.70\n"
        )
        region = _make_table_region("tbl_reg_02", table_text)
        reconstructor = SpatialGridReconstructor()
        header, rows, num_rows, num_cols = reconstructor.reconstruct_grid(region)

        assert num_cols == 3
        assert num_rows == 2
        assert "Standard" in header.flat_column_names[1]
        assert "Limit" in header.flat_column_names[2]
        assert rows[0].cells[0].raw_text == "Piston Clearance"
        assert rows[0].cells[1].raw_text == "0.020 - 0.040"

    def test_subheader_row_detection(self) -> None:
        table_text = (
            "| Component | Torque (N·m) |\n"
            "| --- | --- |\n"
            "| [FRONT SUSPENSION] | |\n"
            "| Strut Mount Nut | 65.0 |\n"
            "| [REAR SUSPENSION] | |\n"
            "| Shock Absorber Bolt | 85.0 |\n"
        )
        region = _make_table_region("tbl_reg_03", table_text)
        reconstructor = SpatialGridReconstructor()
        header, rows, num_rows, num_cols = reconstructor.reconstruct_grid(region)

        assert num_rows == 4
        assert rows[0].is_subheader is True
        assert rows[0].cells[0].raw_text == "[FRONT SUSPENSION]"
        assert rows[1].is_subheader is False
        assert rows[2].is_subheader is True


class TestTableEngineFactory:
    """Test suite for factory and dependency injection."""

    def test_factory_creates_engine(self) -> None:
        engine = AutomotiveTableEngineFactory.create()
        assert isinstance(engine, AutomotiveTableEngine)

    def test_factory_with_custom_config(self) -> None:
        cfg = TableEngineConfig(min_table_confidence=0.85, header_max_depth=3)
        engine = AutomotiveTableEngineFactory.create(config=cfg)
        assert engine.config.min_table_confidence == 0.85
