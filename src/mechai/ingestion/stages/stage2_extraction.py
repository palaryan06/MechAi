"""
Stage 2: Structured Extraction.

Consumes ParsedDocument (Stage 1 output) and produces ExtractedContent:
  - Section hierarchy (from heading elements + markdown heading markers)
  - Procedures (numbered/bulleted lists under procedural headings)
  - Safety warnings (DANGER / WARNING / CAUTION / NOTE blocks)
  - Semantic chunks (aligned to section boundaries, sized for embedding)

Design choices
--------------
The section hierarchy is rebuilt from the markdown export rather than
from the raw element stream. Docling's markdown export reliably preserves
# / ## / ### markers which give unambiguous heading levels. This is
simpler and more robust than inferring levels from font sizes.

Warning detection uses keyword matching on text content. LLM-assisted
extraction is not used in v1 — it would add latency and non-determinism
for something a regex handles well.

Chunking strategy: each section becomes at least one chunk. Long sections
are split at paragraph boundaries with configurable overlap. Chunks carry
their full heading path so the reasoning engine always knows the context.

Extension note: to add torque spec / part number / DTC extraction, add
new extractor methods here and populate the corresponding fields on
ExtractedContent. Prefer adding methods to this class over creating new
stage classes until the extraction logic becomes complex enough to warrant
separation.
"""

from __future__ import annotations

import hashlib
import re
import time

import structlog

from mechai.common.config import IngestionConfig
from mechai.common.exceptions import ExtractionError
from mechai.ingestion.models import (
    DetectedWarning,
    ExtractedContent,
    ExtractionMethod,
    ParsedDocument,
    Procedure,
    ProcedureStep,
    Section,
    SemanticChunk,
    SourceRef,
    WarningSeverity,
)

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------

# Markdown heading: captures level (###) and title text
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")

# Warning keyword at start of line (DANGER, WARNING, CAUTION, NOTE)
_WARNING_RE = re.compile(
    r"^\s*(?:\*\*)?\s*(DANGER|WARNING|CAUTION|NOTE)\b[\s:\-–—]*(.*)$",
    re.IGNORECASE,
)

# Numbered list step: "1. Step text" or "1) Step text"
_NUMBERED_STEP_RE = re.compile(r"^\s*(\d+)[.)]\s+(.+)$")

# Keywords that strongly suggest a heading introduces a procedure
_PROCEDURE_KEYWORDS = frozenset(
    {
        "removal",
        "installation",
        "inspection",
        "replacement",
        "adjustment",
        "bleeding",
        "flushing",
        "torque",
        "procedure",
        "disassembly",
        "assembly",
        "draining",
        "filling",
        "checking",
        "test",
        "testing",
    }
)

_WARNING_SEVERITY_MAP: dict[str, WarningSeverity] = {
    "danger": WarningSeverity.DANGER,
    "warning": WarningSeverity.WARNING,
    "caution": WarningSeverity.CAUTION,
    "note": WarningSeverity.NOTE,
}


# ---------------------------------------------------------------------------
# Helper IDs
# ---------------------------------------------------------------------------


def _section_id(level: int, title: str, page: int) -> str:
    digest = hashlib.md5(f"{level}:{title}:{page}".encode()).hexdigest()[:10]
    return f"sec_{digest}"


def _chunk_id(section_id: str | None, index: int) -> str:
    base = section_id or "doc"
    return f"chunk_{base}_{index}"


def _warning_id(page: int, index: int) -> str:
    return f"warn_p{page}_i{index}"


def _procedure_id(title: str, page: int) -> str:
    digest = hashlib.md5(f"{title}:{page}".encode()).hexdigest()[:10]
    return f"proc_{digest}"


# ---------------------------------------------------------------------------
# ContentExtractor
# ---------------------------------------------------------------------------


class ContentExtractor:
    """
    Stage 2: Structured content extractor.

    Implements ContentExtractorProtocol.
    """

    def __init__(self, config: IngestionConfig | None = None) -> None:
        cfg = config or IngestionConfig()
        self._chunk_max_chars: int = cfg.chunk_max_chars
        self._chunk_overlap_chars: int = cfg.chunk_overlap_chars
        self._min_section_chars: int = cfg.min_section_chars

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract(self, parsed: ParsedDocument) -> ExtractedContent:
        """
        Extract structured content from a ParsedDocument.

        Args:
            parsed: Stage 1 output.

        Returns:
            ExtractedContent with sections, procedures, warnings, and chunks.

        Raises:
            ExtractionError: On unrecoverable extraction failure.
        """
        log = logger.bind(
            stage="stage2_extraction",
            source=str(parsed.source_path),
        )
        log.info("stage_started", page_count=parsed.page_count)
        t0 = time.monotonic()

        try:
            sections = self._extract_sections(parsed)
            warnings = self._extract_warnings(parsed)
            procedures = self._extract_procedures(parsed, sections)
            chunks = self._create_chunks(parsed, sections)
        except Exception as exc:
            log.error("extraction_failed", error=str(exc), exc_info=True)
            raise ExtractionError(f"Structured extraction failed: {exc}") from exc

        elapsed = round(time.monotonic() - t0, 2)
        log.info(
            "stage_completed",
            section_count=len(sections),
            procedure_count=len(procedures),
            warning_count=len(warnings),
            chunk_count=len(chunks),
            duration_seconds=elapsed,
        )

        return ExtractedContent(
            source_path=parsed.source_path,
            page_count=parsed.page_count,
            sections=sections,
            procedures=procedures,
            warnings=warnings,
            tables=parsed.tables,
            chunks=chunks,
        )

    # ------------------------------------------------------------------
    # Section hierarchy from markdown
    # ------------------------------------------------------------------

    def _extract_sections(self, parsed: ParsedDocument) -> list[Section]:
        """
        Rebuild section hierarchy from the markdown export.

        Docling's markdown uses # / ## / ### reliably so we parse the
        heading markers rather than inferring levels from font sizes.
        """
        sections: list[Section] = []
        lines = parsed.raw_markdown.splitlines()

        # Build a simple page estimator: map heading text → page number
        # using the element list from Stage 1.
        heading_to_page: dict[str, int] = {
            e.text.strip(): e.page_number for e in parsed.elements if e.level > 0
        }

        # Track parent stack for hierarchy
        parent_stack: list[tuple[int, str]] = []  # (level, section_id)
        current_page = 1

        for line in lines:
            m = _HEADING_RE.match(line)
            if not m:
                continue

            level = len(m.group(1))  # number of # characters
            title = m.group(2).strip()

            # Best-effort page lookup
            page = heading_to_page.get(title, current_page)

            # Update parent stack
            while parent_stack and parent_stack[-1][0] >= level:
                parent_stack.pop()

            parent_id = parent_stack[-1][1] if parent_stack else None
            sec_id = _section_id(level, title, page)

            source_ref = SourceRef(
                page_number=page,
                extraction_method=ExtractionMethod.HEURISTIC,
                confidence=0.95,
            )
            sections.append(
                Section(
                    section_id=sec_id,
                    title=title,
                    level=level,
                    page_number=page,
                    parent_id=parent_id,
                    source_ref=source_ref,
                )
            )
            parent_stack.append((level, sec_id))
            current_page = page

        return sections

    # ------------------------------------------------------------------
    # Warnings
    # ------------------------------------------------------------------

    def _extract_warnings(self, parsed: ParsedDocument) -> list[DetectedWarning]:
        """
        Detect safety warnings by keyword matching on element text.

        Matches DANGER, WARNING, CAUTION, NOTE at the start of a line
        (with or without markdown bold markers).
        """
        warnings: list[DetectedWarning] = []
        warning_index = 0

        for element in parsed.elements:
            # Check each line in multi-line elements
            for line in element.text.splitlines():
                m = _WARNING_RE.match(line)
                if not m:
                    continue

                keyword = m.group(1).lower()
                rest = m.group(2).strip()
                severity = _WARNING_SEVERITY_MAP.get(keyword, WarningSeverity.NOTE)

                # Combine keyword + rest as warning text
                warning_text = f"{keyword.upper()}: {rest}" if rest else keyword.upper()

                source_ref = SourceRef(
                    page_number=element.page_number,
                    extraction_method=ExtractionMethod.RULE,
                    confidence=1.0,
                )
                warnings.append(
                    DetectedWarning(
                        warning_id=_warning_id(element.page_number, warning_index),
                        severity=severity,
                        text=warning_text,
                        page_number=element.page_number,
                        source_ref=source_ref,
                    )
                )
                warning_index += 1

        return warnings

    # ------------------------------------------------------------------
    # Procedures
    # ------------------------------------------------------------------

    def _extract_procedures(
        self,
        parsed: ParsedDocument,
        sections: list[Section],
    ) -> list[Procedure]:
        """
        Detect repair procedures: numbered/bulleted lists under procedural headings.

        A heading is "procedural" if its title contains a known procedure keyword.
        The steps following the heading (until the next heading) are collected.
        """
        procedures: list[Procedure] = []

        # Build a set of procedural section titles (lower-cased)
        procedural_sections: dict[str, Section] = {
            sec.title.lower(): sec
            for sec in sections
            if any(kw in sec.title.lower() for kw in _PROCEDURE_KEYWORDS)
        }

        if not procedural_sections:
            return procedures

        # Parse markdown line-by-line to collect steps under procedural headings
        lines = parsed.raw_markdown.splitlines()
        active_section: Section | None = None
        pending_steps: list[tuple[int, str]] = []  # (step_number, text)

        def _flush_procedure() -> None:
            nonlocal active_section, pending_steps
            if active_section and pending_steps:
                first_page = active_section.page_number
                source_ref = SourceRef(
                    page_number=first_page,
                    extraction_method=ExtractionMethod.HEURISTIC,
                    confidence=0.9,
                )
                steps = [
                    ProcedureStep(
                        step_number=n,
                        text=t,
                        source_ref=SourceRef(
                            page_number=first_page,
                            extraction_method=ExtractionMethod.HEURISTIC,
                            confidence=0.9,
                        ),
                    )
                    for n, t in pending_steps
                ]
                procedures.append(
                    Procedure(
                        procedure_id=_procedure_id(active_section.title, first_page),
                        title=active_section.title,
                        steps=steps,
                        page_number=first_page,
                        source_ref=source_ref,
                    )
                )
            active_section = None
            pending_steps = []

        for line in lines:
            heading_m = _HEADING_RE.match(line)
            if heading_m:
                _flush_procedure()
                title = heading_m.group(2).strip()
                sec = procedural_sections.get(title.lower())
                if sec is not None:
                    active_section = sec
                continue

            if active_section is not None:
                step_m = _NUMBERED_STEP_RE.match(line)
                if step_m:
                    pending_steps.append((int(step_m.group(1)), step_m.group(2).strip()))

        _flush_procedure()
        return procedures

    # ------------------------------------------------------------------
    # Semantic chunking
    # ------------------------------------------------------------------

    def _create_chunks(
        self,
        parsed: ParsedDocument,
        sections: list[Section],
    ) -> list[SemanticChunk]:
        """
        Produce semantic chunks from the markdown, aligned to section boundaries.

        Algorithm:
          1. Parse the markdown into sections (heading → body text pairs).
          2. Each section body is split into chunks of at most chunk_max_chars.
          3. Chunks carry the full heading path for contextual retrieval.
          4. Short sections (< min_section_chars) are merged into the next chunk.

        The heading path enables the reasoning engine to filter retrieval by
        vehicle system or document section without reading the full chunk text.
        """
        chunks: list[SemanticChunk] = []
        chunk_index = 0

        # Build heading path stack and section_id map
        section_by_title: dict[str, Section] = {s.title: s for s in sections}

        # --- Parse markdown into (heading_path, section_id, page, body) tuples ---
        lines = parsed.raw_markdown.splitlines()
        heading_stack: list[tuple[int, str]] = []  # (level, title)
        current_body: list[str] = []
        current_page = 1
        current_section_id: str | None = None

        # Map heading title → page from parsed elements
        title_to_page: dict[str, int] = {
            e.text.strip(): e.page_number for e in parsed.elements if e.level > 0
        }

        def _emit_chunk(body_text: str, path: list[str], page: int, sec_id: str | None) -> None:
            nonlocal chunk_index
            body_text = body_text.strip()
            if len(body_text) < self._min_section_chars:
                return

            # Split long bodies with overlap
            for segment in self._split_with_overlap(body_text):
                cid = _chunk_id(sec_id, chunk_index)
                source_ref = SourceRef(
                    page_number=page,
                    extraction_method=ExtractionMethod.HEURISTIC,
                    confidence=1.0,
                )
                # Prepend heading path to chunk text for better embedding relevance
                path_prefix = " > ".join(path)
                full_text = f"{path_prefix}\n\n{segment}" if path_prefix else segment

                chunks.append(
                    SemanticChunk(
                        chunk_id=cid,
                        text=full_text,
                        heading_path=list(path),
                        page_number=page,
                        section_id=sec_id,
                        source_ref=source_ref,
                    )
                )
                chunk_index += 1

        for line in lines:
            heading_m = _HEADING_RE.match(line)
            if heading_m:
                # Flush previous section's body
                if current_body:
                    path = [t for _, t in heading_stack]
                    _emit_chunk(
                        "\n".join(current_body),
                        path,
                        current_page,
                        current_section_id,
                    )
                    current_body = []

                level = len(heading_m.group(1))
                title = heading_m.group(2).strip()

                # Maintain heading stack
                while heading_stack and heading_stack[-1][0] >= level:
                    heading_stack.pop()
                heading_stack.append((level, title))

                current_page = title_to_page.get(title, current_page)
                sec = section_by_title.get(title)
                current_section_id = sec.section_id if sec else None
            else:
                stripped = line.strip()
                if stripped:
                    current_body.append(stripped)

        # Flush the last section
        if current_body:
            path = [t for _, t in heading_stack]
            _emit_chunk(
                "\n".join(current_body),
                path,
                current_page,
                current_section_id,
            )

        # Fallback: if the document has no headings, chunk the whole markdown
        if not chunks:
            source_ref = SourceRef(
                page_number=1,
                extraction_method=ExtractionMethod.HEURISTIC,
                confidence=0.7,
            )
            for segment in self._split_with_overlap(parsed.raw_markdown.strip()):
                cid = _chunk_id(None, chunk_index)
                chunks.append(
                    SemanticChunk(
                        chunk_id=cid,
                        text=segment,
                        heading_path=[],
                        page_number=1,
                        section_id=None,
                        source_ref=source_ref,
                    )
                )
                chunk_index += 1

        return chunks

    def _split_with_overlap(self, text: str) -> list[str]:
        """
        Split text into overlapping segments of at most chunk_max_chars.

        Splits at paragraph boundaries (double newline) where possible,
        falling back to character splits if a paragraph is very long.
        """
        if len(text) <= self._chunk_max_chars:
            return [text]

        segments: list[str] = []
        paragraphs = re.split(r"\n{2,}", text)
        current = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            candidate = f"{current}\n\n{para}" if current else para

            if len(candidate) <= self._chunk_max_chars:
                current = candidate
            else:
                if current:
                    segments.append(current)
                    # Overlap: take last overlap_chars of previous chunk
                    overlap_start = max(0, len(current) - self._chunk_overlap_chars)
                    current = current[overlap_start:] + "\n\n" + para
                else:
                    # Single paragraph exceeds max — force-split
                    for i in range(0, len(para), self._chunk_max_chars - self._chunk_overlap_chars):
                        segments.append(para[i : i + self._chunk_max_chars])
                    current = ""

        if current.strip():
            segments.append(current)

        return segments or [text]
