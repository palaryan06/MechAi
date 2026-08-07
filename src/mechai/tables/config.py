"""Configuration models for Automotive Table Intelligence Engine (RFC-AUTO-001).

Calibrated geometric, clustering, unit matching, and multi-page continuation thresholds.
All models are strictly typed and immutable (frozen=True).
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class TableEngineConfig(BaseModel):
    """Configuration thresholds governing deterministic table grid reconstruction."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    min_table_confidence: Annotated[
        float, Field(ge=0.0, le=1.0, default=0.70, description="Minimum confidence for valid table")
    ]
    column_gap_min_pt: Annotated[
        float, Field(gt=0.0, default=10.0, description="Minimum whitespace gap in points between columns")
    ]
    row_vertical_gap_max_pt: Annotated[
        float, Field(gt=0.0, default=16.0, description="Maximum vertical gap between text lines in same row")
    ]
    header_max_depth: Annotated[
        int, Field(ge=1, le=8, default=4, description="Maximum depth of hierarchical multi-row headers")
    ]
    header_similarity_threshold: Annotated[
        float, Field(ge=0.0, le=1.0, default=0.70, description="Jaccard similarity threshold for multi-page headers")
    ]
    max_continuation_page_gap: Annotated[
        int, Field(ge=1, le=5, default=1, description="Maximum allowed page gap for continued tables")
    ]
    merge_unbordered_rows_tolerance_pt: Annotated[
        float, Field(gt=0.0, default=4.0, description="Y-tolerance for grouping words into row baselines")
    ]
    align_numeric_right: bool = Field(
        default=True,
        description="Whether numeric data cells should be classified with CellAlignment.RIGHT",
    )
    align_center_threshold_chars: Annotated[
        int, Field(ge=1, default=15, description="Max char length for center alignment candidate")
    ]
