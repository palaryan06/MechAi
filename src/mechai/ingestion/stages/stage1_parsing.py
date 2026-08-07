"""
Stage 1: Document Parsing using Docling.

Docling (IBM Research, v2.x) was chosen over PyMuPDF / pdfplumber because:
  - Native layout classification (title, section_header, text, list, table, figure)
  - Accurate table extraction with cell structure
  - Heading hierarchy inference
  - Single-library call replaces the planned Stage 1 + Stage 2 in the original
    16-stage design, saving significant implementation time with better results.

Evaluation notes
----------------
Docling 2.x uses a heuristic pipeline by default (no GPU required) which
produces accurate results on digitally-created PDFs like workshop manuals.
OCR mode (use_ocr=True) is available for scanned documents via tesseract/
rapidocr but is not needed for standard workshop manual PDFs.

If Docling fails on a specific PDF, the exception is wrapped in
DocumentParseError so the pipeline can handle it uniformly.

Extension note: to support additional input formats (DOCX, HTML), configure
Docling with the appropriate allowed_formats. The rest of the pipeline is
format-agnostic since it operates on ParsedDocument.
"""

from __future__ import annotations

import hashlib
import tempfile
import time
from pathlib import Path
from typing import Any

import structlog

from mechai.common.exceptions import DocumentParseError
from mechai.ingestion.models import (
    BoundingBox,
    ExtractionMethod,
    ParsedDocument,
    SourceRef,
    TableElement,
    TextElement,
    TextElementLabel,
)

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Docling label → our TextElementLabel
# ---------------------------------------------------------------------------

_LABEL_MAP: dict[str, TextElementLabel] = {
    "title": TextElementLabel.TITLE,
    "section_header": TextElementLabel.SECTION_HEADER,
    "text": TextElementLabel.TEXT,
    "paragraph": TextElementLabel.TEXT,
    "list_item": TextElementLabel.LIST_ITEM,
    "caption": TextElementLabel.CAPTION,
    "page_header": TextElementLabel.PAGE_HEADER,
    "page_footer": TextElementLabel.PAGE_FOOTER,
    "code": TextElementLabel.CODE,
    "formula": TextElementLabel.FORMULA,
    "footnote": TextElementLabel.FOOTNOTE,
}

# Labels that carry no document-content value and are skipped
_SKIP_LABELS = {TextElementLabel.PAGE_HEADER, TextElementLabel.PAGE_FOOTER}


def _make_element_id(page: int, index: int, text: str) -> str:
    digest = hashlib.md5(f"{page}:{index}:{text[:64]}".encode()).hexdigest()[:12]
    return f"elem_{digest}"


def _make_table_id(page: int, index: int) -> str:
    return f"table_p{page}_i{index}"


def _get_label(item: Any) -> TextElementLabel:
    """Safely extract and map a Docling label to TextElementLabel."""
    raw = getattr(item, "label", None)
    if raw is None:
        return TextElementLabel.OTHER
    # DocItemLabel is an Enum — get its value string
    label_str = raw.value if hasattr(raw, "value") else str(raw)
    return _LABEL_MAP.get(label_str.lower(), TextElementLabel.OTHER)


def _get_page_and_bbox(item: Any) -> tuple[int, BoundingBox | None]:
    """Extract page number and bounding box from a Docling item's prov list."""
    prov_list = getattr(item, "prov", None) or []
    if not prov_list:
        return 1, None

    prov = prov_list[0]
    page_no: int = int(getattr(prov, "page_no", 1))

    bbox_obj = getattr(prov, "bbox", None)
    bbox: BoundingBox | None = None
    if bbox_obj is not None:
        try:
            bbox = BoundingBox(
                left=float(getattr(bbox_obj, "l", 0)),
                top=float(getattr(bbox_obj, "t", 0)),
                right=float(getattr(bbox_obj, "r", 0)),
                bottom=float(getattr(bbox_obj, "b", 0)),
            )
        except (TypeError, ValueError):
            pass

    return page_no, bbox


class DoclingParser:
    """
    Stage 1: PDF parser backed by Docling.

    Implements PdfParserProtocol.

    Docling is initialised lazily on first parse() call to avoid slow import
    at module load time during testing.
    """

    def __init__(
        self,
        *,
        use_ocr: bool = False,
        artifacts_path: Path | None = None,
    ) -> None:
        """
        Args:
            use_ocr: Enable OCR (requires tesseract or rapidocr to be installed).
            artifacts_path: Optional local path for Docling model cache.
        """
        self._use_ocr = use_ocr
        self._artifacts_path = artifacts_path
        self._converter: Any = None  # lazy

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse(self, source: Path | bytes) -> ParsedDocument:
        """
        Parse a PDF document using Docling.

        Args:
            source: Path to PDF, or raw PDF bytes.

        Returns:
            ParsedDocument with text elements, tables, and markdown export.

        Raises:
            DocumentParseError: If Docling fails for any reason.
        """
        log = logger.bind(stage="stage1_parsing")
        source_path = source if isinstance(source, Path) else Path("in-memory.pdf")
        log = log.bind(source=str(source_path))
        log.info("stage_started")
        t0 = time.monotonic()

        tmp_path: Path | None = None
        try:
            converter = self._get_converter()

            if isinstance(source, bytes):
                # Docling requires a file path; write to a temp file
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    tmp.write(source)
                    tmp_path = Path(tmp.name)
                conversion_source: str = str(tmp_path)
            else:
                if not source.exists():
                    raise DocumentParseError(f"PDF file not found: {source}")
                conversion_source = str(source)

            result = converter.convert(conversion_source)
            doc = result.document

        except DocumentParseError:
            raise
        except Exception as exc:
            log.error("docling_failed", error=str(exc), exc_info=True)
            raise DocumentParseError(f"Docling could not parse the PDF: {exc}") from exc
        finally:
            if tmp_path is not None:
                tmp_path.unlink(missing_ok=True)

        elements = self._extract_text_elements(doc, log)
        tables = self._extract_tables(doc, log)

        # Page count: use Docling's pages dict; fall back to max page seen
        page_count = (
            len(doc.pages)
            if getattr(doc, "pages", None)
            else (max((e.page_number for e in elements), default=1))
        )

        # Document title: first TITLE element
        title: str | None = next(
            (e.text for e in elements if e.label == TextElementLabel.TITLE), None
        )

        raw_markdown: str = doc.export_to_markdown()

        elapsed = round(time.monotonic() - t0, 2)
        log.info(
            "stage_completed",
            page_count=page_count,
            element_count=len(elements),
            table_count=len(tables),
            duration_seconds=elapsed,
        )

        return ParsedDocument(
            source_path=source_path,
            page_count=page_count,
            title=title,
            raw_markdown=raw_markdown,
            elements=elements,
            tables=tables,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_converter(self) -> Any:
        """Lazily create and cache the Docling DocumentConverter."""
        if self._converter is not None:
            return self._converter

        try:
            from docling.datamodel.pipeline_options import PdfPipelineOptions
            from docling.document_converter import DocumentConverter
        except ImportError as exc:
            raise DocumentParseError("Docling is not installed. Run: pip install docling") from exc

        opts = PdfPipelineOptions()
        opts.do_ocr = self._use_ocr
        opts.do_table_structure = True
        opts.table_structure_options.do_cell_matching = True

        self._converter = DocumentConverter()
        logger.info("docling_converter_ready", use_ocr=self._use_ocr)
        return self._converter

    def _extract_text_elements(self, doc: Any, log: Any) -> list[TextElement]:
        """Extract typed text elements from a DoclingDocument."""
        elements: list[TextElement] = []

        try:
            for index, item in enumerate(doc.texts):
                label = _get_label(item)

                # Skip purely structural labels that add no content value
                if label in _SKIP_LABELS:
                    continue

                text: str = (getattr(item, "text", "") or "").strip()
                if not text:
                    continue

                page_no, bbox = _get_page_and_bbox(item)

                # Heading level: titles are level 1, section headers level 2+
                # Docling doesn't always expose a numeric level, so we use
                # label-based defaults; Stage 2 refines these from markdown.
                level = 0
                if label == TextElementLabel.TITLE:
                    level = 1
                elif label == TextElementLabel.SECTION_HEADER:
                    level = 2  # Stage 2 will assign precise levels from markdown

                source_ref = SourceRef(
                    page_number=page_no,
                    extraction_method=ExtractionMethod.DOCLING,
                    confidence=1.0,
                    bbox=bbox,
                )
                elements.append(
                    TextElement(
                        element_id=_make_element_id(page_no, index, text),
                        text=text,
                        label=label,
                        page_number=page_no,
                        level=level,
                        source_ref=source_ref,
                    )
                )

        except Exception as exc:
            log.warning("text_element_extraction_partial_failure", error=str(exc))

        return elements

    def _extract_tables(self, doc: Any, log: Any) -> list[TableElement]:
        """Extract structured tables from a DoclingDocument."""
        tables: list[TableElement] = []

        try:
            for index, table_item in enumerate(doc.tables):
                page_no, _ = _get_page_and_bbox(table_item)

                # Caption: Docling stores captions as refs to text items
                caption: str | None = None
                for cap_ref in getattr(table_item, "captions", []):
                    try:
                        cap_item = cap_ref.resolve(doc)
                        if cap_item and getattr(cap_item, "text", ""):
                            caption = cap_item.text.strip()
                            break
                    except Exception:
                        pass

                headers: list[str] = []
                rows: list[list[str]] = []

                table_data = getattr(table_item, "data", None)
                if table_data is not None:
                    grid: list[Any] = getattr(table_data, "grid", []) or []
                    if grid:
                        # Check if first row contains header cells
                        first_row: list[Any] = grid[0]
                        is_header = any(
                            getattr(cell, "column_header", False)
                            or getattr(cell, "row_header", False)
                            for cell in first_row
                        )
                        if is_header:
                            headers = [(getattr(c, "text", "") or "").strip() for c in first_row]
                            data_rows = grid[1:]
                        else:
                            data_rows = grid

                        for row in data_rows:
                            rows.append([(getattr(c, "text", "") or "").strip() for c in row])

                source_ref = SourceRef(
                    page_number=page_no,
                    extraction_method=ExtractionMethod.DOCLING,
                    confidence=1.0,
                )
                tables.append(
                    TableElement(
                        table_id=_make_table_id(page_no, index),
                        caption=caption,
                        headers=headers,
                        rows=rows,
                        page_number=page_no,
                        source_ref=source_ref,
                    )
                )

        except Exception as exc:
            log.warning("table_extraction_partial_failure", error=str(exc))

        return tables
