"""Configuration models for the document parsing engine."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path  # noqa: TC003
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ParserBackend(StrEnum):
    """Supported document parsing engine backends."""

    AUTO = "auto"
    PYMUPDF = "pymupdf"
    DOCLING = "docling"


class DocumentParserConfig(BaseModel):
    """Configuration options for document parsing execution."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    backend: ParserBackend = ParserBackend.AUTO
    extract_images: bool = True
    extract_words: bool = True
    image_output_dir: Path | None = None
    max_pages: Annotated[int, Field(ge=1)] | None = None
    start_page: Annotated[int, Field(ge=1)] = 1
    min_word_length: Annotated[int, Field(ge=1)] = 1
    dpi: Annotated[int, Field(ge=72, le=600)] = 150
    timeout_seconds: Annotated[float, Field(gt=0.0)] = 300.0
