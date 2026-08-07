"""Document parsing backend integrating IBM Docling (v2.x)."""

from __future__ import annotations

import time
from pathlib import Path

import structlog

from mechai.common.exceptions import DocumentParseError
from mechai.contracts.scrubbing import ParsedDocument, ParsedImage, ParsedPage, ParsedWord
from mechai.ingestion.parsing.base import DocumentParser
from mechai.ingestion.parsing.config import DocumentParserConfig  # noqa: TC001
from mechai.ingestion.parsing.result import ParserMetrics, ParserResult

logger = structlog.get_logger(__name__)


class DoclingParser(DocumentParser):
    """Stage 1 PDF parser backend utilizing IBM Docling.

    Converts PDFs using Docling layout models and bridges the representation into
    canonical MechAI ParsedDocument instances.
    """

    def __init__(self, config: DocumentParserConfig | None = None) -> None:
        """Initialize Docling parser with configuration and verify dependency."""
        super().__init__(config=config)
        self._check_dependency()

    def _check_dependency(self) -> None:
        """Verify that docling package is installed."""
        try:
            import docling  # type: ignore[import-not-found] # noqa: F401
        except ImportError as exc:
            msg = (
                "Docling backend requires 'docling' library. "
                "Install it via 'pip install docling' or configure ParserBackend.PYMUPDF."
            )
            raise DocumentParseError(msg) from exc

    def parse(self, source: str | Path | bytes) -> ParsedDocument:
        """Parse raw PDF file or bytes into a structured ParsedDocument."""
        result = self.parse_with_result(source)
        return result.document

    def parse_with_result(self, source: str | Path | bytes) -> ParserResult:
        """Parse PDF with Docling and return structured ParserResult."""
        from docling.datamodel.base_models import InputFormat  # type: ignore[import-not-found]
        from docling.document_converter import DocumentConverter  # type: ignore[import-not-found]

        start_time = time.perf_counter()
        temp_file_path: Path | None = None
        source_path_str: str | None = None

        try:
            if isinstance(source, bytes):
                if not source:
                    raise DocumentParseError("Provided PDF byte buffer is empty.")
                import tempfile

                temp_file = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
                temp_file.write(source)
                temp_file.flush()
                temp_file.close()
                temp_file_path = Path(temp_file.name)
                conv_source = temp_file_path
            else:
                path = Path(source)
                if not path.exists():
                    raise DocumentParseError(f"PDF source file does not exist: {path}")
                source_path_str = str(path.resolve())
                conv_source = path

            converter = DocumentConverter(allowed_formats=[InputFormat.PDF])
            conv_result = converter.convert(conv_source)
            docling_doc = conv_result.document

            parsed_pages_dict: dict[int, list[ParsedWord]] = {}
            parsed_images_dict: dict[int, list[ParsedImage]] = {}
            page_text_dict: dict[int, list[str]] = {}
            page_dims: dict[int, tuple[float, float]] = {}

            # Populate page dimensions if available
            for p_no, page_meta in getattr(docling_doc, "pages", {}).items():
                size = getattr(page_meta, "size", None)
                if size:
                    page_dims[p_no] = (float(size.width), float(size.height))

            # Iterate texts in document
            for item, _level in docling_doc.iterate_items():
                text = getattr(item, "text", "") or ""
                prov_list = getattr(item, "prov", None) or []
                page_no = 1
                bbox_obj = None

                if prov_list:
                    prov = prov_list[0]
                    page_no = int(getattr(prov, "page_no", 1))
                    bbox_obj = getattr(prov, "bbox", None)

                if page_no not in page_text_dict:
                    page_text_dict[page_no] = []
                    parsed_pages_dict[page_no] = []
                    parsed_images_dict[page_no] = []

                if text:
                    page_text_dict[page_no].append(text)
                    words_in_text = text.split()
                    for w in words_in_text:
                        left = float(bbox_obj.l) if bbox_obj else 0.0
                        top = float(bbox_obj.t) if bbox_obj else 0.0
                        right = float(bbox_obj.r) if bbox_obj else 0.0
                        bottom = float(bbox_obj.b) if bbox_obj else 0.0
                        parsed_pages_dict[page_no].append(
                            ParsedWord(
                                text=w,
                                left=left,
                                top=top,
                                right=right,
                                bottom=bottom,
                            )
                        )

            # Build canonical ParsedPage list
            all_page_numbers = sorted(set(page_dims.keys()) | set(page_text_dict.keys()) | {1})
            parsed_pages: list[ParsedPage] = []
            total_words = 0

            for p_num in all_page_numbers:
                w_list = parsed_pages_dict.get(p_num, [])
                total_words += len(w_list)
                p_text = "\n".join(page_text_dict.get(p_num, []))
                p_width, p_height = page_dims.get(p_num, (612.0, 792.0))

                parsed_pages.append(
                    ParsedPage(
                        page_number=p_num,
                        text=p_text,
                        words=tuple(w_list),
                        images=tuple(parsed_images_dict.get(p_num, [])),
                        width=p_width,
                        height=p_height,
                    )
                )

            elapsed_seconds = time.perf_counter() - start_time
            elapsed_ms = elapsed_seconds * 1000.0
            pages_processed = len(parsed_pages)
            pages_per_sec = (
                (pages_processed / elapsed_seconds) if elapsed_seconds > 0 else float("inf")
            )

            metrics = ParserMetrics(
                elapsed_ms=elapsed_ms,
                pages_per_sec=pages_per_sec,
                page_count=pages_processed,
                word_count=total_words,
                image_count=0,
                backend="docling",
            )

            return ParserResult(
                document=ParsedDocument(
                    pages=tuple(parsed_pages),
                    source_path=source_path_str,
                ),
                metrics=metrics,
                metadata={"title": getattr(docling_doc, "name", None)},
            )

        except DocumentParseError:
            raise
        except Exception as exc:
            raise DocumentParseError(f"Docling conversion failed: {exc}") from exc
        finally:
            if temp_file_path and temp_file_path.exists():
                try:
                    temp_file_path.unlink()
                except OSError:
                    pass
