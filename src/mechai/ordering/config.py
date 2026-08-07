"""Configuration models for Reading Order Engine (Stage 2.1).

RFC-008: Configurable parameters governing spatial band slicing, caption binding,
callout prioritization, sidebar branching, and graph generation.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ReadingOrderConfig(BaseModel):
    """Configuration governing spatial sorting heuristics and reading order graph generation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    caption_max_distance_pt: float = Field(
        default=36.0,
        gt=0.0,
        description="Max distance in points between a visual region and its caption",
    )
    band_vertical_overlap_ratio: float = Field(
        default=0.30,
        ge=0.0,
        le=1.0,
        description="Vertical overlap threshold used to group multi-column elements into bands",
    )
    warning_precedence_boost: bool = Field(
        default=True,
        description="Whether callouts are prioritized ahead of adjacent steps",
    )
    header_footer_isolation: bool = Field(
        default=True,
        description="Whether running headers/footers are detached from primary flow",
    )
    cross_page_continuity: bool = Field(
        default=True,
        description="Whether cross-page flow edges are generated between consecutive pages",
    )
    min_edge_confidence: float = Field(
        default=0.70,
        ge=0.0,
        le=1.0,
        description="Baseline epistemic confidence for standard geometric reading transitions",
    )
