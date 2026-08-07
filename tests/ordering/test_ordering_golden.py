"""Golden reference tests for Reading Order Engine (Stage 2.1)."""

from __future__ import annotations

import json
from pathlib import Path

from mechai.contracts.layout import LayoutCIR
from mechai.contracts.ordering import OrderedLayoutCIR
from mechai.ordering import ReadingOrderEngineFactory

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
LAYOUT_GOLDEN_JSON = FIXTURES_DIR / "sample_manual_layout_golden.json"


class TestReadingOrderGoldenFile:
    """Validate Reading Order output against standardized layout golden references."""

    def test_reading_order_matches_golden_reference(self) -> None:
        """Process golden LayoutCIR and assert strict reading order invariants."""
        assert LAYOUT_GOLDEN_JSON.exists(), f"Missing golden layout fixture at {LAYOUT_GOLDEN_JSON}"

        with open(LAYOUT_GOLDEN_JSON, encoding="utf-8") as f:
            layout_data = json.load(f)

        layout_cir = LayoutCIR.model_validate(layout_data)
        assert layout_cir.total_pages == 2

        engine = ReadingOrderEngineFactory.create()
        ordered_cir: OrderedLayoutCIR = engine.order_layout(layout_cir)

        assert isinstance(ordered_cir, OrderedLayoutCIR)
        assert ordered_cir.total_pages == 2

        # Verify page 1
        p1 = ordered_cir.pages[0]
        assert p1.page_number == 1
        assert p1.primary_sequence[0] == "reg_p1_001"  # Title
        assert p1.reading_order_graph.is_dag is True

        # Verify page 2
        p2 = ordered_cir.pages[1]
        assert p2.page_number == 2
        assert p2.reading_order_graph.is_dag is True

        # Verify global graph
        assert ordered_cir.global_graph.is_dag is True
        assert len(ordered_cir.global_graph.primary_path) == len(p1.primary_sequence) + len(
            p2.primary_sequence
        )
