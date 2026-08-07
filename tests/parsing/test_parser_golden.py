"""Golden file regression tests for the Document Parsing Engine."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mechai.contracts.scrubbing import ParsedDocument
from mechai.ingestion.parsing import PyMuPDFParser

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
SAMPLE_PDF = FIXTURES_DIR / "sample_manual.pdf"
GOLDEN_JSON = FIXTURES_DIR / "sample_manual_golden.json"


class TestParserGoldenFile:
    """Regression test suite validating deterministic parsing output against golden references."""

    def test_parsed_output_matches_golden_reference(self) -> None:
        assert SAMPLE_PDF.exists(), f"Fixture PDF missing: {SAMPLE_PDF}"
        assert GOLDEN_JSON.exists(), f"Golden reference JSON missing: {GOLDEN_JSON}"

        parser = PyMuPDFParser()
        result = parser.parse_with_result(SAMPLE_PDF)
        actual_doc = result.document

        # Load golden dictionary
        with open(GOLDEN_JSON, encoding="utf-8") as f:
            golden_data = json.load(f)

        expected_doc = ParsedDocument.model_validate(golden_data)

        # 1. Compare page counts
        assert actual_doc.total_pages == expected_doc.total_pages

        # 2. Compare page-by-page attributes
        for p_idx, (actual_p, expected_p) in enumerate(
            zip(actual_doc.pages, expected_doc.pages, strict=True)
        ):
            assert actual_p.page_number == expected_p.page_number
            assert actual_p.width == pytest.approx(expected_p.width or 0.0)
            assert actual_p.height == pytest.approx(expected_p.height or 0.0)
            assert actual_p.text == expected_p.text

            # Compare words
            assert len(actual_p.words) == len(expected_p.words)
            for w_idx, (act_w, exp_w) in enumerate(
                zip(actual_p.words, expected_p.words, strict=True)
            ):
                err_msg = f"Word mismatch at p{p_idx + 1} w{w_idx}: {act_w.text} != {exp_w.text}"
                assert act_w.text == exp_w.text, err_msg
                assert act_w.left == pytest.approx(exp_w.left, abs=1e-3)
                assert act_w.top == pytest.approx(exp_w.top, abs=1e-3)
                assert act_w.right == pytest.approx(exp_w.right, abs=1e-3)
                assert act_w.bottom == pytest.approx(exp_w.bottom, abs=1e-3)
                assert act_w.bold == exp_w.bold
                assert act_w.italic == exp_w.italic

            # Compare images
            assert len(actual_p.images) == len(expected_p.images)
            for act_img, exp_img in zip(actual_p.images, expected_p.images, strict=True):
                assert act_img.width == exp_img.width
                assert act_img.height == exp_img.height
                if exp_img.bbox is not None and act_img.bbox is not None:
                    assert act_img.bbox.left == pytest.approx(exp_img.bbox.left, abs=1e-3)
                    assert act_img.bbox.top == pytest.approx(exp_img.bbox.top, abs=1e-3)
                    assert act_img.bbox.right == pytest.approx(exp_img.bbox.right, abs=1e-3)
                    assert act_img.bbox.bottom == pytest.approx(exp_img.bbox.bottom, abs=1e-3)
