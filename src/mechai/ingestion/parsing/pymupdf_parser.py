"""High-performance PDF parser backend utilizing PyMuPDF (fitz)."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import fitz  # type: ignore[import-untyped]
import structlog

from mechai.common.exceptions import DocumentParseError
from mechai.contracts.provenance import BoundingBox
from mechai.contracts.scrubbing import ParsedDocument, ParsedImage, ParsedPage, ParsedWord
from mechai.ingestion.parsing.base import DocumentParser
from mechai.ingestion.parsing.config import DocumentParserConfig  # noqa: TC001
from mechai.ingestion.parsing.result import ParserMetrics, ParserResult

logger = structlog.get_logger(__name__)


class PyMuPDFParser(DocumentParser):
    """Stage 1 PDF parser implementation powered by PyMuPDF.

    Extracts text tokens with exact bounding boxes, font attributes (size, font name, bold,
    italic), embedded images with geometry, page dimensions, and document metadata with
    sub-millisecond per-page efficiency.
    """

    def __init__(self, config: DocumentParserConfig | None = None) -> None:
        """Initialize PyMuPDF parser with configuration."""
        super().__init__(config=config)

    def parse(self, source: str | Path | bytes) -> ParsedDocument:
        """Parse raw PDF file or bytes into a structured ParsedDocument."""
        result = self.parse_with_result(source)
        return result.document

    def parse_with_result(self, source: str | Path | bytes) -> ParserResult:
        """Parse raw PDF and return detailed ParserResult with metrics and metadata."""
        start_time = time.perf_counter()
        source_path_str: str | None = None
        doc: fitz.Document | None = None

        try:
            if isinstance(source, bytes):
                if not source:
                    raise DocumentParseError("Provided PDF byte buffer is empty.")
                doc = fitz.open(stream=source, filetype="pdf")
            else:
                path = Path(source)
                if not path.exists():
                    raise DocumentParseError(f"PDF source file does not exist: {path}")
                if not path.is_file():
                    raise DocumentParseError(f"PDF source path is not a file: {path}")
                source_path_str = str(path.resolve())
                doc = fitz.open(source_path_str)

            total_doc_pages = len(doc)
            if total_doc_pages == 0:
                raise DocumentParseError("PDF document contains zero pages.")

            # Compute page processing range (1-indexed input)
            start_idx = max(0, self._config.start_page - 1)
            end_idx = total_doc_pages
            if self._config.max_pages is not None:
                end_idx = min(total_doc_pages, start_idx + self._config.max_pages)

            if start_idx >= total_doc_pages:
                msg = (
                    f"start_page ({self._config.start_page}) "
                    f"exceeds total pages ({total_doc_pages})."
                )
                raise DocumentParseError(msg)

            parsed_pages: list[ParsedPage] = []
            total_words_extracted = 0
            total_images_extracted = 0

            # Ensure image output directory exists if configured
            if self._config.image_output_dir is not None:
                self._config.image_output_dir.mkdir(parents=True, exist_ok=True)

            for page_idx in range(start_idx, end_idx):
                page_num = page_idx + 1
                page = doc.load_page(page_idx)
                page_rect = page.rect
                page_width = float(page_rect.width)
                page_height = float(page_rect.height)
                page_text = page.get_text("text")

                words: list[ParsedWord] = []
                if self._config.extract_words:
                    words = self._extract_page_words(page)
                    total_words_extracted += len(words)

                images: list[ParsedImage] = []
                if self._config.extract_images:
                    images = self._extract_page_images(doc, page, page_num)
                    total_images_extracted += len(images)

                parsed_pages.append(
                    ParsedPage(
                        page_number=page_num,
                        text=page_text,
                        words=tuple(words),
                        images=tuple(images),
                        width=page_width,
                        height=page_height,
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
                word_count=total_words_extracted,
                image_count=total_images_extracted,
                backend="pymupdf",
            )

            metadata = self._extract_doc_metadata(doc)

            parsed_doc = ParsedDocument(
                pages=tuple(parsed_pages),
                source_path=source_path_str,
            )

            logger.info(
                "pdf_parsing_complete",
                pages=pages_processed,
                words=total_words_extracted,
                images=total_images_extracted,
                elapsed_ms=round(elapsed_ms, 2),
                pages_per_sec=round(pages_per_sec, 2),
            )

            return ParserResult(
                document=parsed_doc,
                metrics=metrics,
                metadata=metadata,
            )

        except fitz.FileDataError as exc:
            raise DocumentParseError(f"Corrupt or invalid PDF data: {exc}") from exc
        except DocumentParseError:
            raise
        except Exception as exc:
            raise DocumentParseError(f"Unexpected error during PDF parsing: {exc}") from exc
        finally:
            if doc is not None:
                doc.close()

    def _extract_page_words(self, page: fitz.Page) -> list[ParsedWord]:
        """Extract word tokens from page with typography flags and exact bounding boxes."""
        words: list[ParsedWord] = []
        page_dict: dict[str, Any] = page.get_text("dict", flags=fitz.TEXT_DEHYPHENATE)

        for block in page_dict.get("blocks", []):
            if block.get("type") != 0:  # Text block
                continue

            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    span_text: str = span.get("text", "")
                    if not span_text.strip():
                        continue

                    font_name: str | None = span.get("font")
                    font_size: float | None = span.get("size")
                    flags: int = span.get("flags", 0)

                    # Determine bold and italic from flags or font name heuristics
                    is_italic = bool(flags & 2) or bool(
                        font_name and any(k in font_name.lower() for k in ("italic", "oblique"))
                    )
                    is_bold = bool(flags & 16) or bool(
                        font_name
                        and any(k in font_name.lower() for k in ("bold", "black", "heavy"))
                    )

                    # Extract words within the span
                    span_bbox = span.get("bbox", (0.0, 0.0, 0.0, 0.0))
                    span_words = span_text.split()
                    if not span_words:
                        continue

                    # If single word in span, bbox is exact span bbox
                    if len(span_words) == 1:
                        w_text = span_words[0]
                        if len(w_text) >= self._config.min_word_length:
                            words.append(
                                ParsedWord(
                                    text=w_text,
                                    left=float(span_bbox[0]),
                                    top=float(span_bbox[1]),
                                    right=float(span_bbox[2]),
                                    bottom=float(span_bbox[3]),
                                    font_size=font_size,
                                    font_name=font_name,
                                    bold=is_bold,
                                    italic=is_italic,
                                )
                            )
                    else:
                        # Estimate proportional word bboxes across the span width
                        total_chars = max(1, len(span_text))
                        span_width = span_bbox[2] - span_bbox[0]
                        char_width = span_width / total_chars

                        curr_pos = 0
                        for w_text in span_words:
                            w_idx = span_text.find(w_text, curr_pos)
                            if w_idx == -1:
                                w_idx = curr_pos

                            w_start_x = span_bbox[0] + (w_idx * char_width)
                            w_end_x = w_start_x + (len(w_text) * char_width)
                            curr_pos = w_idx + len(w_text)

                            if len(w_text) >= self._config.min_word_length:
                                words.append(
                                    ParsedWord(
                                        text=w_text,
                                        left=float(w_start_x),
                                        top=float(span_bbox[1]),
                                        right=float(w_end_x),
                                        bottom=float(span_bbox[3]),
                                        font_size=font_size,
                                        font_name=font_name,
                                        bold=is_bold,
                                        italic=is_italic,
                                    )
                                )

        return words

    def _extract_page_images(
        self, doc: fitz.Document, page: fitz.Page, page_num: int
    ) -> list[ParsedImage]:
        """Extract embedded image metadata and bounding boxes from a page."""
        images: list[ParsedImage] = []
        image_info_list = page.get_images(full=True)

        for img_idx, img_info in enumerate(image_info_list):
            xref = img_info[0]
            img_width = img_info[2]
            img_height = img_info[3]
            img_format = img_info[8]  # compression filter / format name

            # Derive bounding box on page
            bbox: BoundingBox | None = None
            rects = page.get_image_rects(xref)
            if rects:
                rect = rects[0]
                bbox = BoundingBox(
                    left=float(rect.x0),
                    top=float(rect.y0),
                    right=float(rect.x1),
                    bottom=float(rect.y1),
                )

            image_id = f"img_p{page_num}_{img_idx + 1}_{xref}"
            file_path_str: str | None = None

            # Save image bytes if output directory configured
            if self._config.image_output_dir is not None:
                try:
                    pix = fitz.Pixmap(doc, xref)
                    if pix.n >= 5:  # CMYK or other -> convert to RGB
                        pix = fitz.Pixmap(fitz.csRGB, pix)
                    out_ext = "png"
                    out_filename = f"{image_id}.{out_ext}"
                    out_path = self._config.image_output_dir / out_filename
                    pix.save(str(out_path))
                    file_path_str = str(out_path.resolve())
                except Exception as exc:
                    logger.warning(
                        "image_extraction_save_failed",
                        image_id=image_id,
                        error=str(exc),
                    )

            images.append(
                ParsedImage(
                    image_id=image_id,
                    bbox=bbox,
                    width=img_width if img_width > 0 else None,
                    height=img_height if img_height > 0 else None,
                    image_format=str(img_format) if img_format else None,
                    file_path=file_path_str,
                )
            )

        return images

    def _extract_doc_metadata(self, doc: fitz.Document) -> dict[str, Any]:
        """Extract sanitized metadata dictionary from PDF document."""
        meta = doc.metadata or {}
        return {
            "title": meta.get("title") or None,
            "author": meta.get("author") or None,
            "subject": meta.get("subject") or None,
            "keywords": meta.get("keywords") or None,
            "creator": meta.get("creator") or None,
            "producer": meta.get("producer") or None,
            "creation_date": meta.get("creationDate") or None,
            "mod_date": meta.get("modDate") or None,
            "format": meta.get("format") or "PDF",
            "page_count": len(doc),
        }
