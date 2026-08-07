"""Execution results and performance telemetry for the document parsing engine."""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field

from mechai.contracts.scrubbing import ParsedDocument  # noqa: TC001


class ParserMetrics(BaseModel):
    """Performance and throughput metrics collected during parsing."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    elapsed_ms: Annotated[float, Field(ge=0.0)]
    pages_per_sec: Annotated[float, Field(ge=0.0)]
    page_count: Annotated[int, Field(ge=0)]
    word_count: Annotated[int, Field(ge=0)]
    image_count: Annotated[int, Field(ge=0)]
    backend: str = Field(min_length=1)


class ParserResult(BaseModel):
    """Complete output of document parsing including structured document and telemetry."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    document: ParsedDocument
    metrics: ParserMetrics
    metadata: dict[str, Any] = Field(default_factory=dict)
