"""Tests for data_cleaning.config module."""

from __future__ import annotations

import pytest

from data_cleaning.config import DataCleaningConfig


class TestDataCleaningConfig:
    """Test cases for DataCleaningConfig dataclass."""

    def test_default_values(self):
        """Test that default values are correctly set."""
        cfg = DataCleaningConfig()

        assert cfg.rpm_max == 10_000
        assert cfg.efficiency_min == 75.0
        assert cfg.efficiency_max == 100.0
        assert cfg.spindles_per_side == 84
        assert cfg.shift_hours == 8.0
        assert cfg.drop_multi_style_shifts is True

    def test_default_column_names(self):
        """Test that default column names are correctly set."""
        cfg = DataCleaningConfig()

        assert cfg.col_date == "Date"
        assert cfg.col_shift == "Shift_period"
        assert cfg.col_machine == "Machine-number"
        assert cfg.col_style == "Style-description"
        assert cfg.col_runtime == "Run_time"
        assert cfg.col_rpm == "RPM"

    def test_custom_values(self):
        """Test that custom values override defaults."""
        cfg = DataCleaningConfig(
            rpm_max=9000,
            efficiency_min=70.0,
            efficiency_max=95.0,
            spindles_per_side=100,
            shift_hours=12.0,
            drop_multi_style_shifts=False,
        )

        assert cfg.rpm_max == 9000
        assert cfg.efficiency_min == 70.0
        assert cfg.efficiency_max == 95.0
        assert cfg.spindles_per_side == 100
        assert cfg.shift_hours == 12.0
        assert cfg.drop_multi_style_shifts is False

    def test_rename_map_set_in_post_init(self):
        """Test that rename_map is automatically populated in __post_init__."""
        cfg = DataCleaningConfig()

        assert cfg.rename_map is not None
        assert cfg.rename_map == {
            "Shift\nperiod": "Shift_period",
            "Run\ntime": "Run_time",
        }

    def test_frozen_dataclass(self):
        """Test that the config is immutable (frozen)."""
        cfg = DataCleaningConfig()

        with pytest.raises(AttributeError):
            cfg.rpm_max = 5000  # type: ignore[misc]

    def test_custom_column_names(self):
        """Test that custom column names can be specified."""
        cfg = DataCleaningConfig(
            col_date="MyDate",
            col_shift="MyShift",
            col_machine="MyMachine",
            col_style="MyStyle",
            col_runtime="MyRuntime",
            col_rpm="MyRPM",
        )

        assert cfg.col_date == "MyDate"
        assert cfg.col_shift == "MyShift"
        assert cfg.col_machine == "MyMachine"
        assert cfg.col_style == "MyStyle"
        assert cfg.col_runtime == "MyRuntime"
        assert cfg.col_rpm == "MyRPM"
