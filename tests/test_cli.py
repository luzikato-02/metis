"""Tests for data_cleaning.cli module."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from data_cleaning.cli import build_parser, main

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


class TestBuildParser:
    """Test cases for build_parser function."""

    def test_parser_creation(self):
        """Test that parser is created successfully."""
        parser = build_parser()
        assert parser is not None
        assert parser.prog == "data-clean"

    def test_required_positional_args(self):
        """Test that input and output are required positional arguments."""
        parser = build_parser()

        # Should fail without arguments
        with pytest.raises(SystemExit):
            parser.parse_args([])

        # Should fail with only one argument
        with pytest.raises(SystemExit):
            parser.parse_args(["input.csv"])

    def test_positional_args_parsing(self):
        """Test parsing of positional arguments."""
        parser = build_parser()
        args = parser.parse_args(["input.csv", "output.csv"])

        assert args.input == "input.csv"
        assert args.output == "output.csv"

    def test_default_values(self):
        """Test default values for optional arguments."""
        parser = build_parser()
        args = parser.parse_args(["input.csv", "output.csv"])

        assert args.input_format is None
        assert args.output_format is None
        assert args.rpm_max == 10_000
        assert args.eff_min == 75.0
        assert args.eff_max == 100.0
        assert args.spindles == 84
        assert args.shift_hours == 8.0
        assert args.keep_multi_style_shifts is False

    def test_custom_rpm_max(self):
        """Test custom rpm-max argument."""
        parser = build_parser()
        args = parser.parse_args(["input.csv", "output.csv", "--rpm-max", "9000"])

        assert args.rpm_max == 9000.0

    def test_custom_efficiency_range(self):
        """Test custom efficiency range arguments."""
        parser = build_parser()
        args = parser.parse_args([
            "input.csv", "output.csv",
            "--eff-min", "70",
            "--eff-max", "95",
        ])

        assert args.eff_min == 70.0
        assert args.eff_max == 95.0

    def test_custom_spindles(self):
        """Test custom spindles argument."""
        parser = build_parser()
        args = parser.parse_args(["input.csv", "output.csv", "--spindles", "100"])

        assert args.spindles == 100

    def test_custom_shift_hours(self):
        """Test custom shift-hours argument."""
        parser = build_parser()
        args = parser.parse_args(["input.csv", "output.csv", "--shift-hours", "12"])

        assert args.shift_hours == 12.0

    def test_keep_multi_style_shifts_flag(self):
        """Test keep-multi-style-shifts flag."""
        parser = build_parser()
        args = parser.parse_args(["input.csv", "output.csv", "--keep-multi-style-shifts"])

        assert args.keep_multi_style_shifts is True

    def test_format_override_args(self):
        """Test input/output format override arguments."""
        parser = build_parser()
        args = parser.parse_args([
            "input.data", "output.out",
            "--input-format", "csv",
            "--output-format", "parquet",
        ])

        assert args.input_format == "csv"
        assert args.output_format == "parquet"


class TestMain:
    """Test cases for main function."""

    def test_successful_execution(self, valid_raw_dataframe):
        """Test successful CLI execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.csv"
            output_path = Path(tmpdir) / "output.csv"

            valid_raw_dataframe.to_csv(input_path, index=False)

            result = main([str(input_path), str(output_path)])

            assert result == 0
            assert output_path.exists()

    def test_with_custom_options(self, valid_raw_dataframe):
        """Test CLI with custom options."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.csv"
            output_path = Path(tmpdir) / "output.csv"

            valid_raw_dataframe.to_csv(input_path, index=False)

            result = main([
                str(input_path),
                str(output_path),
                "--rpm-max", "6000",
                "--eff-min", "0",
                "--eff-max", "100",
            ])

            assert result == 0
            df_output = pd.read_csv(output_path)
            assert (df_output["RPM"] <= 6000).all()

    def test_with_format_override(self, valid_raw_dataframe):
        """Test CLI with format override."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.data"
            output_path = Path(tmpdir) / "output.out"

            valid_raw_dataframe.to_csv(input_path, index=False)

            result = main([
                str(input_path),
                str(output_path),
                "--input-format", "csv",
                "--output-format", "csv",
            ])

            assert result == 0
            assert output_path.exists()

    def test_keep_multi_style_shifts(self, valid_raw_dataframe):
        """Test CLI with keep-multi-style-shifts option."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.csv"
            output_path = Path(tmpdir) / "output.csv"

            valid_raw_dataframe.to_csv(input_path, index=False)

            result = main([
                str(input_path),
                str(output_path),
                "--keep-multi-style-shifts",
            ])

            assert result == 0
            assert output_path.exists()

    def test_missing_input_file_raises_error(self):
        """Test that missing input file raises an error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "nonexistent.csv"
            output_path = Path(tmpdir) / "output.csv"

            with pytest.raises(FileNotFoundError):
                main([str(input_path), str(output_path)])

    def test_invalid_columns_raises_error(self):
        """Test that invalid columns raise an error."""
        df_incomplete = pd.DataFrame({
            "Date": ["2024-01-01"],
            "Shift_period": ["Day"],
        })

        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.csv"
            output_path = Path(tmpdir) / "output.csv"

            df_incomplete.to_csv(input_path, index=False)

            with pytest.raises(KeyError, match="Missing required columns"):
                main([str(input_path), str(output_path)])


class TestCLIIntegration:
    """Integration tests for CLI."""

    def test_full_pipeline_csv(self, valid_raw_dataframe):
        """Test full pipeline with CSV files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.csv"
            output_path = Path(tmpdir) / "output.csv"

            valid_raw_dataframe.to_csv(input_path, index=False)

            result = main([str(input_path), str(output_path)])

            assert result == 0
            df_output = pd.read_csv(output_path)

            # Check that derived columns are present
            assert "Run_time_seconds" in df_output.columns
            assert "Machine_Efficiency" in df_output.columns

    @pytest.mark.skipif(not HAS_PARQUET, reason="pyarrow or fastparquet not installed")
    def test_full_pipeline_parquet(self, valid_raw_dataframe):
        """Test full pipeline with Parquet files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            input_path = Path(tmpdir) / "input.parquet"
            output_path = Path(tmpdir) / "output.parquet"

            valid_raw_dataframe.to_parquet(input_path, index=False)

            result = main([str(input_path), str(output_path)])

            assert result == 0
            df_output = pd.read_parquet(output_path)

            assert "Run_time_seconds" in df_output.columns
            assert "Machine_Efficiency" in df_output.columns
