"""Golden file regression tests for Stage 2.0 Layout Intelligence Engine."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mechai.contracts.layout import LayoutCIR
from mechai.ingestion.parsing import PyMuPDFParser
from mechai.layout import LayoutEngineFactory

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
SAMPLE_PDF = FIXTURES_DIR / "sample_manual.pdf"
GOLDEN_LAYOUT_JSON = FIXTURES_DIR / "sample_manual_layout_golden.json"


class TestLayoutGoldenFile:
    """Golden regression tests validating deterministic layout output against frozen reference."""

    def test_layout_segmentation_matches_golden_reference(self) -> None:
        assert SAMPLE_PDF.exists(), f"Fixture PDF missing: {SAMPLE_PDF}"

        parser = PyMuPDFParser()
        parsed_doc = parser.parse(SAMPLE_PDF)

        engine = LayoutEngineFactory.create()
        actual_layout = engine.segment_layout(parsed_doc)

        # Generate golden if missing
        if not GOLDEN_LAYOUT_JSON.exists():
            with open(GOLDEN_LAYOUT_JSON, "w", encoding="utf-8") as f:
                json.dump(actual_layout.model_dump(mode="json"), f, indent=2)

        # Load golden dictionary
        with open(GOLDEN_LAYOUT_JSON, encoding="utf-8") as f:
            golden_data = json.load(f)

        expected_layout = LayoutCIR.model_validate(golden_data)

        # 1. Compare page counts and metadata
        assert actual_layout.total_pages == expected_layout.total_pages
        assert len(actual_layout.pages) == len(expected_layout.pages)

        # 2. Compare page-by-page layout zones & regions
        for p_idx, (actual_p, expected_p) in enumerate(
            zip(actual_layout.pages, expected_layout.pages, strict=True)
        ):
            assert actual_p.page_number == expected_p.page_number
            assert actual_p.width == pytest.approx(expected_p.width)
            assert actual_p.height == pytest.approx(expected_p.height)
            assert actual_p.margins.left == pytest.approx(expected_p.margins.left)
            assert actual_p.margins.top == pytest.approx(expected_p.margins.top)
            assert actual_p.margins.right == pytest.approx(expected_p.margins.right)
            assert actual_p.margins.bottom == pytest.approx(expected_p.margins.bottom)

            # Compare columns
            assert len(actual_p.columns) == len(expected_p.columns)
            for act_col, exp_col in zip(actual_p.columns, expected_p.columns, strict=True):
                assert act_col.left == pytest.approx(exp_col.left)
                assert act_col.right == pytest.approx(exp_col.right)

            # Compare regions
            assert len(actual_p.regions) == len(expected_p.regions)
            for r_idx, (act_r, exp_r) in enumerate(
                zip(actual_p.regions, expected_p.regions, strict=True)
            ):
                err_msg = f"Region mismatch at p{p_idx + 1} r{r_idx}: {act_r.id} vs {exp_r.id}"
                assert act_r.id == exp_r.id, err_msg
                assert act_r.region_type == exp_r.region_type, err_msg
                assert act_r.confidence == pytest.approx(exp_r.confidence, abs=1e-2), err_msg
                assert act_r.bbox.left == pytest.approx(exp_r.bbox.left, abs=1e-2), err_msg
                assert act_r.bbox.top == pytest.approx(exp_r.bbox.top, abs=1e-2), err_msg
                assert act_r.bbox.right == pytest.approx(exp_r.bbox.right, abs=1e-2), err_msg
                assert act_r.bbox.bottom == pytest.approx(exp_r.bbox.bottom, abs=1e-2), err_msg
                assert act_r.text == exp_r.text, err_msg
                assert act_r.reading_zone_id == exp_r.reading_zone_id, err_msg
                assert act_r.column_index == exp_r.column_index, err_msg
