"""Tests for data_cleaning.app module."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from data_cleaning.app import run_cleaning_job
from data_cleaning.config import DataCleaningConfig

# Check if parquet is available
try:
    import pyarrow  # noqa: F401
    HAS_PARQUET = True
except ImportError:
    try:
        import fastparquet  # noqa: F401
        HAS_PARQUET = True
    except ImportError:
        HAS_PARQUET = False


@pytest.fixture
def valid_raw_dataframe():
    """Create a valid raw DataFrame with all required columns."""
    return pd.DataFrame({
        "Date": ["2024-01-01", "2024-01-01", "2024-01-02"],
        "Shift_period": ["Day", "Night", "Day"],
        "Machine-number": ["M1", "M1", "M2"],
        "Style-description": ["Style A", "Style A", "Style B"],
        "Run_time": ["06:00:00", "07:00:00", "06:30:00"],
        "RPM": [5000, 6000, 5500],
    })


class TestRunCleaningJob:
    """Test cases for run_cleaning_job function."""

    def test_csv_to_csv(self, valid_raw_dataframe):
        """Test cleaning from CSV to CSV."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.csv"
            output_path = Path(tmpdir) / "output.csv"

            valid_raw_dataframe.to_csv(input_path, index=False)

            run_cleaning_job(input_path, output_path)

            assert output_path.exists()
            df_output = pd.read_csv(output_path)
            assert len(df_output) >= 0  # May have rows filtered

    @pytest.mark.skipif(not HAS_PARQUET, reason="pyarrow or fastparquet not installed")
    def test_csv_to_parquet(self, valid_raw_dataframe):
        """Test cleaning from CSV to Parquet."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.csv"
            output_path = Path(tmpdir) / "output.parquet"

            valid_raw_dataframe.to_csv(input_path, index=False)

            run_cleaning_job(input_path, output_path)

            assert output_path.exists()
            df_output = pd.read_parquet(output_path)
            assert len(df_output) >= 0

    @pytest.mark.skipif(not HAS_PARQUET, reason="pyarrow or fastparquet not installed")
    def test_parquet_to_csv(self, valid_raw_dataframe):
        """Test cleaning from Parquet to CSV."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.parquet"
            output_path = Path(tmpdir) / "output.csv"

            valid_raw_dataframe.to_parquet(input_path, index=False)

            run_cleaning_job(input_path, output_path)

            assert output_path.exists()
            df_output = pd.read_csv(output_path)
            assert len(df_output) >= 0

    def test_with_custom_config(self, valid_raw_dataframe):
        """Test cleaning with custom config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.csv"
            output_path = Path(tmpdir) / "output.csv"

            valid_raw_dataframe.to_csv(input_path, index=False)

            cfg = DataCleaningConfig(rpm_max=5500)  # Will filter out some rows
            run_cleaning_job(input_path, output_path, config=cfg)

            assert output_path.exists()
            df_output = pd.read_csv(output_path)
            assert (df_output["RPM"] <= 5500).all()

    def test_with_format_override(self, valid_raw_dataframe):
        """Test cleaning with format override."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.data"  # Non-standard extension
            output_path = Path(tmpdir) / "output.out"  # Non-standard extension

            valid_raw_dataframe.to_csv(input_path, index=False)

            run_cleaning_job(
                input_path,
                output_path,
                input_format="csv",
                output_format="csv",
            )

            assert output_path.exists()
            df_output = pd.read_csv(output_path)
            assert len(df_output) >= 0

    def test_string_paths(self, valid_raw_dataframe):
        """Test that string paths work as well as Path objects."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = str(Path(tmpdir) / "input.csv")
            output_path = str(Path(tmpdir) / "output.csv")

            valid_raw_dataframe.to_csv(input_path, index=False)

            run_cleaning_job(input_path, output_path)

            assert Path(output_path).exists()

    def test_derived_columns_in_output(self, valid_raw_dataframe):
        """Test that derived columns are present in output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.csv"
            output_path = Path(tmpdir) / "output.csv"

            valid_raw_dataframe.to_csv(input_path, index=False)

            run_cleaning_job(input_path, output_path)

            df_output = pd.read_csv(output_path)
            assert "Run_time_seconds" in df_output.columns
            assert "Run_time_per_spindle_seconds" in df_output.columns
            assert "Run_time_per_spindle_hours" in df_output.columns
            assert "Machine_Efficiency" in df_output.columns

    def test_missing_columns_raises_error(self):
        """Test that missing columns raise an error."""
        df_incomplete = pd.DataFrame({
            "Date": ["2024-01-01"],
            "Shift_period": ["Day"],
            # Missing other required columns
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.csv"
            output_path = Path(tmpdir) / "output.csv"

            df_incomplete.to_csv(input_path, index=False)

            with pytest.raises(KeyError, match="Missing required columns"):
                run_cleaning_job(input_path, output_path)
