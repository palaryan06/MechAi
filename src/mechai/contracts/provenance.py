"""Provenance data contracts shared across all ingestion stages."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ExtractionMethod(StrEnum):
    """Extraction mechanism that produced a specific artifact."""

    RULE = "rule"
    HEURISTIC = "heuristic"
    LLM = "llm"
    DOCLING = "docling"
    OCR = "ocr"


class BoundingBox(BaseModel):
    """Bounding box coordinates on a document page (in points from page origin)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    left: float
    top: float
    right: float
    bottom: float

    @property
    def width(self) -> float:
        """Bounding box width."""
        return max(0.0, self.right - self.left)

    @property
    def height(self) -> float:
        """Bounding box height."""
        return max(0.0, self.bottom - self.top)

    @property
    def center_x(self) -> float:
        """Horizontal midpoint coordinate."""
        return (self.left + self.right) / 2.0

    @property
    def center_y(self) -> float:
        """Vertical midpoint coordinate."""
        return (self.top + self.bottom) / 2.0


class SourceRef(BaseModel):
    """Full provenance reference grounding an extracted artifact in source material.

    Attributes:
        page_number: 1-based page number in the original PDF.
        extraction_method: Method used to extract this artifact.
        confidence: Extraction confidence score (0.0 to 1.0).
        bbox: Optional physical bounding box on the page.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    page_number: Annotated[int, Field(ge=1)]
    extraction_method: ExtractionMethod = ExtractionMethod.RULE
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] = 1.0
    bbox: BoundingBox | None = None
