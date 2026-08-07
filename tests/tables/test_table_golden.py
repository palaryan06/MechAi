"""Golden regression tests for Automotive Table Intelligence Engine (RFC-AUTO-001).

Tests schema conformance, serialization/deserialization fidelity, contract immutability,
and round-tripping of structured automotive tables.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from mechai.contracts.tables import (
    AutomotiveTable,
    AutomotiveTableCell,
    AutomotiveTableFootnote,
    AutomotiveTableHeader,
    AutomotiveTableRow,
    AutomotiveTableSet,
    AutomotiveTableType,
    CellAlignment,
    CellType,
)
from mechai.layout.factory import LayoutEngineFactory
from mechai.ordering.factory import ReadingOrderEngineFactory
from mechai.ingestion.parsing.factory import ParserFactory
from mechai.tables.factory import AutomotiveTableEngineFactory

_FIXTURES_DIR = Path(__file__).resolve().parent.parent / "fixtures"
_SAMPLE_PDF = _FIXTURES_DIR / "sample_manual.pdf"


class TestAutomotiveTableGolden:
    """Golden test suite verifying strict contracts and serializability."""

    def test_immutability_enforcement(self) -> None:
        """Verify that all table contracts are strictly frozen."""
        cell = AutomotiveTableCell(
            cell_id="c_01",
            row_index=0,
            col_index=0,
            raw_text="50 N·m",
            normalized_text="50 N·m",
            cell_type=CellType.DATA,
            alignment=CellAlignment.RIGHT,
            bbox={"left": 10.0, "top": 20.0, "right": 50.0, "bottom": 30.0},
            page_number=1,
            confidence=0.98,
            provenance={"page_number": 1, "extraction_method": "rule", "confidence": 0.98},
            reading_order_ref="reg_01",
        )

        with pytest.raises(ValidationError):
            cell.raw_text = "60 N·m"  # type: ignore[misc]

        row = AutomotiveTableRow(
            row_index=0,
            cells=(cell,),
        )
        with pytest.raises(ValidationError):
            row.is_subheader = True  # type: ignore[misc]

        header = AutomotiveTableHeader(
            header_rows=((cell,),),
            flat_column_names=("Torque",),
            depth=1,
        )
        with pytest.raises(ValidationError):
            header.depth = 2  # type: ignore[misc]

    def test_json_roundtrip_serialization(self) -> None:
        """Verify full round-trip JSON serialization and deserialization."""
        parser = ParserFactory.create()
        parsed = parser.parse(_SAMPLE_PDF)
        zoner = LayoutEngineFactory.create()
        layout_cir = zoner.process(parsed)
        order_engine = ReadingOrderEngineFactory.create()
        ordered_cir = order_engine.order_layout(layout_cir)

        table_engine = AutomotiveTableEngineFactory.create()
        table_set = table_engine.reconstruct_tables(ordered_cir)

        # Serialize to JSON
        json_data = table_set.model_dump_json(indent=2)
        assert isinstance(json_data, str)
        assert len(json_data) > 100

        # Deserialize back
        reloaded_dict = json.loads(json_data)
        reloaded_table_set = AutomotiveTableSet.model_validate(reloaded_dict)

        assert reloaded_table_set.document_id == table_set.document_id
        assert reloaded_table_set.total_tables == table_set.total_tables
        assert len(reloaded_table_set.tables) == len(table_set.tables)

        for orig_t, rel_t in zip(table_set.tables, reloaded_table_set.tables, strict=True):
            assert orig_t.table_id == rel_t.table_id
            assert orig_t.table_type == rel_t.table_type
            assert orig_t.num_columns == rel_t.num_columns
            assert orig_t.num_rows == rel_t.num_rows
            assert orig_t.header.flat_column_names == rel_t.header.flat_column_names
