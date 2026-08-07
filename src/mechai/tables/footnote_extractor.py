"""Automotive Footnote and Annotation Extractor (RFC-AUTO-001).

Deterministic identification and association of table footnotes, qualification markers,
and subscript/superscript qualifiers (*1, (a), [1], †, ‡) found in OEM service manuals.
"""

from __future__ import annotations

import re

from mechai.contracts.provenance import SourceRef
from mechai.contracts.tables import AutomotiveTableFootnote

# Footnote Marker Patterns (e.g. *1, *2, **, (a), [1], †, ‡)
_FOOTNOTE_MARKER_RE = re.compile(
    r"""(?x)
    (?:
        \*{1,3}\d*|              # *, **, ***, *1, *2
        \([a-z0-9]\)|             # (a), (b), (1), (2)
        \[[a-z0-9]\]|             # [a], [1]
        [†‡§#]                   # Dagger, double dagger, section, hash
    )
    """,
    re.IGNORECASE,
)

# Footnote Definition Line Pattern (e.g. "*1: Replace with new part", "(a) Tighten with engine cold")
_FOOTNOTE_DEF_RE = re.compile(
    r"""(?xi)
    ^\s*
    (?P<marker>
        \*{1,3}\d*|
        \([a-z0-9]\)|
        \[[a-z0-9]\]|
        [†‡§#]
    )
    \s*[:\-\.]?\s+
    (?P<text>.+)$
    """
)


class AutomotiveFootnoteExtractor:
    """Deterministic extractor for table footnotes and cell qualifier references."""

    @staticmethod
    def extract_cell_markers(text: str) -> tuple[str, ...]:
        """Extract all footnote markers referenced within a cell's text."""
        if not text:
            return ()

        matches = _FOOTNOTE_MARKER_RE.findall(text)
        # Filter duplicates while preserving order
        seen: set[str] = set()
        unique_markers: list[str] = []
        for m in matches:
            clean = m.strip()
            if clean and clean not in seen:
                seen.add(clean)
                unique_markers.append(clean)

        return tuple(unique_markers)

    @staticmethod
    def parse_footnote_lines(
        lines: list[str],
        page_number: int,
        provenance: SourceRef,
    ) -> list[AutomotiveTableFootnote]:
        """Parse footnote definition lines into AutomotiveTableFootnote models."""
        footnotes: list[AutomotiveTableFootnote] = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            match = _FOOTNOTE_DEF_RE.match(stripped)
            if match:
                marker = match.group("marker").strip()
                def_text = match.group("text").strip()
                footnotes.append(
                    AutomotiveTableFootnote(
                        marker=marker,
                        text=def_text,
                        page_number=page_number,
                        provenance=provenance,
                    )
                )
            elif stripped.startswith(("*", "Note:", "NOTE:")) and not footnotes:
                # General asterisk note without formal colon delimiter
                marker = "*"
                def_text = stripped.lstrip("*: ").strip()
                if def_text:
                    footnotes.append(
                        AutomotiveTableFootnote(
                            marker=marker,
                            text=def_text,
                            page_number=page_number,
                            provenance=provenance,
                        )
                    )

        return footnotes
