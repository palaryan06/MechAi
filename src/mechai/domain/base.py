"""Base models and foundational value objects for the domain layer.

All domain models inherit from DomainModel, enforcing immutability (frozen=True),
strict typing, and clean serialization without external runtime dependencies.
"""

from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class DomainModel(BaseModel):
    """Base class for all automotive domain entities and value objects.

    Enforces immutability, forbids unvalidated fields, and standardizes serialization.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class DomainProvenance(DomainModel):
    """Grounding provenance indicating the origin of a domain entity.

    Attributes:
        manual_id: Optional identifier of the source manual.
        section_id: Optional identifier of the source section.
        page_number: 1-based page number in the original publication.
        source_label: Optional label/reference (e.g., 'Table 5-2', 'Step 4b').
        confidence: Optional confidence score for extracted/inferred facts.
    """

    manual_id: str | None = None
    section_id: str | None = None
    page_number: int | None = Field(default=None, ge=1)
    source_label: str | None = None
    confidence: Annotated[float, Field(ge=0.0, le=1.0)] | None = None
