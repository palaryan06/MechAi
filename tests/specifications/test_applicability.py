"""Tests for applicability context extraction and merging."""

import pytest

from mechai.specifications.applicability import ApplicabilityResolver
from mechai.contracts.specifications import ApplicabilityContext


class TestApplicability:
    """Test extracting and merging applicability contexts."""

    @pytest.fixture
    def resolver(self) -> ApplicabilityResolver:
        return ApplicabilityResolver()

    def test_extract_transmission(self, resolver: ApplicabilityResolver) -> None:
        """Test extracting transmission types."""
        ctx1 = resolver.extract_from_text("For A/T only")
        assert ctx1.transmission == "A/T"
        
        ctx2 = resolver.extract_from_text("M/T vehicle")
        assert ctx2.transmission == "M/T"

    def test_extract_engine(self, resolver: ApplicabilityResolver) -> None:
        """Test extracting engine codes."""
        ctx = resolver.extract_from_text("Suzuki K10B engine")
        assert ctx.engine_code == "K10B"

    def test_merge_contexts(self, resolver: ApplicabilityResolver) -> None:
        """Test merging contexts from parent and child."""
        base = ApplicabilityContext(engine_code="K10B", transmission="A/T")
        override = ApplicabilityContext(transmission="M/T", variant="with A/C")
        
        merged = resolver.merge_contexts(base, override)
        
        # Engine code should be inherited
        assert merged.engine_code == "K10B"
        # Transmission should be overridden by child
        assert merged.transmission == "M/T"
        # Variant should be added from child
        assert merged.variant == "with A/C"
