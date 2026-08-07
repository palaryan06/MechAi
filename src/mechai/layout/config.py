"""Configuration parameters for Layout Intelligence Engine (Stage 2.0).

Calibrated geometric and typographic thresholds governing zoning, column slicing,
and region classification.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LayoutZonerConfig(BaseModel):
    """Immutable configuration for GeometricLayoutZoner."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    # Header & Footer geometric boundaries (as ratio of page height)
    header_max_y_ratio: float = Field(
        default=0.09,
        ge=0.02,
        le=0.25,
        description="Maximum y-ratio for running header zone candidate detection",
    )
    footer_min_y_ratio: float = Field(
        default=0.92,
        ge=0.75,
        le=0.98,
        description="Minimum y-ratio for running footer zone candidate detection",
    )

    # Margin bounds (in points)
    min_margin_pt: float = Field(
        default=18.0,
        ge=0.0,
        le=100.0,
        description="Minimum margin padding from page boundary in points",
    )
    default_margin_pt: float = Field(
        default=36.0,
        ge=0.0,
        le=150.0,
        description="Default fallback margin when page has no tokens",
    )

    # Multi-column detection thresholds
    min_gutter_width_pt: float = Field(
        default=10.0,
        ge=4.0,
        le=50.0,
        description="Minimum horizontal whitespace gap to qualify as a column gutter",
    )
    histogram_bin_size_pt: float = Field(
        default=2.0,
        ge=0.5,
        le=10.0,
        description="Spatial bin size in points for vertical projection profile histogram",
    )
    spanning_block_width_ratio: float = Field(
        default=0.75,
        ge=0.5,
        le=1.0,
        description="Width ratio above which a block is considered spanning multiple columns",
    )

    # Line and block clustering tolerances
    line_vertical_tolerance_pt: float = Field(
        default=3.5,
        ge=1.0,
        le=10.0,
        description="Vertical center distance tolerance to group words into the same text line",
    )
    block_line_gap_ratio: float = Field(
        default=1.75,
        ge=1.0,
        le=3.5,
        description="Max vertical gap as a multiple of line height to group lines into blocks",
    )

    # Typographic classification font scale ratios (relative to estimated body font size)
    title_font_scale: float = Field(
        default=1.45,
        ge=1.2,
        le=3.0,
        description="Font size multiplier threshold to classify a region as Title",
    )
    heading_font_scale: float = Field(
        default=1.20,
        ge=1.1,
        le=2.0,
        description="Font size multiplier threshold to classify a region as Heading",
    )
    subheading_font_scale: float = Field(
        default=1.05,
        ge=1.0,
        le=1.5,
        description="Font size multiplier threshold to classify a region as Subheading",
    )
    default_body_font_size: float = Field(
        default=10.0,
        ge=4.0,
        le=24.0,
        description="Fallback baseline body font size in points",
    )

    # Sidebar width threshold
    sidebar_max_width_ratio: float = Field(
        default=0.35,
        ge=0.1,
        le=0.5,
        description="Maximum body width ratio for narrow sidebar column classification",
    )
