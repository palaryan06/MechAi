"""Tests for the unit normalization subsystem."""

import pytest
from mechai.specifications.unit_normalizer import UnitNormalizer


class TestUnitNormalization:
    """Ensure raw values correctly map to canonical representations."""

    @pytest.fixture
    def normalizer(self) -> UnitNormalizer:
        return UnitNormalizer()

    def test_torque_normalization(self, normalizer: UnitNormalizer) -> None:
        """Test kgf-m to N.m conversion."""
        result = normalizer.extract_specification_value("4.5 kgf-m")
        assert result is not None
        assert result.raw_value == "4.5 kgf-m"
        assert result.numeric_value == 4.5
        assert result.original_unit == "kgf-m"
        assert result.canonical_unit == "N.m"
        # 4.5 * 9.80665 = 44.129925
        assert result.canonical_value is not None
        assert abs(result.canonical_value - 44.13) < 0.01

    def test_ft_lb_normalization(self, normalizer: UnitNormalizer) -> None:
        """Test ft-lb to N.m conversion."""
        result = normalizer.extract_specification_value("33 ft-lb")
        assert result is not None
        assert result.numeric_value == 33.0
        assert result.canonical_unit == "N.m"
        # 33 * 1.355818 = 44.742
        assert result.canonical_value is not None
        assert abs(result.canonical_value - 44.74) < 0.01

    def test_clearance_normalization(self, normalizer: UnitNormalizer) -> None:
        """Test mm normalization."""
        result = normalizer.extract_specification_value("0.15 mm")
        assert result is not None
        assert result.numeric_value == 0.15
        assert result.canonical_unit == "mm"
        assert result.canonical_value == 0.15

    def test_range_parsing(self, normalizer: UnitNormalizer) -> None:
        """Test parsing a range string like '0.13 - 0.17 mm'."""
        result = normalizer.extract_specification_value("0.13 - 0.17 mm")
        assert result is not None
        assert result.numeric_value is None
        assert result.tolerance_min == 0.13
        assert result.tolerance_max == 0.17
        assert result.canonical_unit == "mm"

    def test_tolerance_parsing(self, normalizer: UnitNormalizer) -> None:
        """Test parsing a tolerance string like '45 +/- 2 N.m'."""
        result = normalizer.extract_specification_value("45 +/- 2 N.m")
        assert result is not None
        assert result.numeric_value == 45.0
        assert result.tolerance_min == 43.0
        assert result.tolerance_max == 47.0
        assert result.canonical_unit == "N.m"

    def test_unknown_unit_retains_number(self, normalizer: UnitNormalizer) -> None:
        """Test that unknown units don't crash and still extract the number."""
        result = normalizer.extract_specification_value("45 apples")
        # Assuming the normalizer matches "45" and treats "apples" as non-unit,
        # or matches the numeric pattern if no unit pattern matches.
        # Given our current regex, "apples" won't match the standard units list
        # if we only do specific matches. But our regex is broad for value_with_unit_pattern.
        # It captures any letters as unit. 
        # Then _find_rule fails, it returns None canonical unit.
        assert result is not None
        assert result.numeric_value == 45.0
        assert result.canonical_unit is None

    def test_unitless_number(self, normalizer: UnitNormalizer) -> None:
        """Test extracting a standalone number."""
        result = normalizer.extract_specification_value("45")
        assert result is not None
        assert result.numeric_value == 45.0
        assert result.canonical_unit is None
        assert result.original_unit is None
