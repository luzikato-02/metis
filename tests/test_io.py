"""Tests for data_cleaning.io module."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from data_cleaning.io import read_input_file, write_output_file

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
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    return pd.DataFrame({
        "A": [1, 2, 3],
        "B": ["x", "y", "z"],
        "C": [1.1, 2.2, 3.3],
    })


class TestReadInputFile:
    """Test cases for read_input_file function."""

    def test_read_csv(self, sample_dataframe):
        """Test reading a CSV file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            sample_dataframe.to_csv(f.name, index=False)
            temp_path = Path(f.name)

        try:
            df = read_input_file(temp_path)
            pd.testing.assert_frame_equal(df, sample_dataframe)
        finally:
            temp_path.unlink()

    def test_read_csv_with_format_override(self, sample_dataframe):
        """Test reading a file with format override."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".data", delete=False) as f:
            sample_dataframe.to_csv(f.name, index=False)
            temp_path = Path(f.name)

        try:
            df = read_input_file(temp_path, fmt="csv")
            pd.testing.assert_frame_equal(df, sample_dataframe)
        finally:
            temp_path.unlink()

    @pytest.mark.skipif(not HAS_PARQUET, reason="pyarrow or fastparquet not installed")
    def test_read_parquet(self, sample_dataframe):
        """Test reading a Parquet file."""
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            sample_dataframe.to_parquet(f.name, index=False)
            temp_path = Path(f.name)

        try:
            df = read_input_file(temp_path)
            pd.testing.assert_frame_equal(df, sample_dataframe)
        finally:
            temp_path.unlink()

    def test_unsupported_format_raises_error(self):
        """Test that unsupported format raises ValueError."""
        with tempfile.NamedTemporaryFile(suffix=".unsupported", delete=False) as f:
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Unsupported input format"):
                read_input_file(temp_path)
        finally:
            temp_path.unlink()

    def test_read_with_string_path(self, sample_dataframe):
        """Test reading using string path instead of Path object."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            sample_dataframe.to_csv(f.name, index=False)
            temp_path = f.name

        try:
            df = read_input_file(temp_path)
            pd.testing.assert_frame_equal(df, sample_dataframe)
        finally:
            Path(temp_path).unlink()


class TestWriteOutputFile:
    """Test cases for write_output_file function."""

    def test_write_csv(self, sample_dataframe):
        """Test writing a CSV file."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_path = Path(f.name)

        try:
            write_output_file(sample_dataframe, temp_path)
            df = pd.read_csv(temp_path)
            pd.testing.assert_frame_equal(df, sample_dataframe)
        finally:
            temp_path.unlink()

    def test_write_csv_with_format_override(self, sample_dataframe):
        """Test writing a file with format override."""
        with tempfile.NamedTemporaryFile(suffix=".data", delete=False) as f:
            temp_path = Path(f.name)

        try:
            write_output_file(sample_dataframe, temp_path, fmt="csv")
            df = pd.read_csv(temp_path)
            pd.testing.assert_frame_equal(df, sample_dataframe)
        finally:
            temp_path.unlink()

    @pytest.mark.skipif(not HAS_PARQUET, reason="pyarrow or fastparquet not installed")
    def test_write_parquet(self, sample_dataframe):
        """Test writing a Parquet file."""
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            temp_path = Path(f.name)

        try:
            write_output_file(sample_dataframe, temp_path)
            df = pd.read_parquet(temp_path)
            pd.testing.assert_frame_equal(df, sample_dataframe)
        finally:
            temp_path.unlink()

    def test_write_with_index(self, sample_dataframe):
        """Test writing with index=True."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_path = Path(f.name)

        try:
            write_output_file(sample_dataframe, temp_path, index=True)
            df = pd.read_csv(temp_path, index_col=0)
            pd.testing.assert_frame_equal(df, sample_dataframe)
        finally:
            temp_path.unlink()

    def test_unsupported_format_raises_error(self, sample_dataframe):
        """Test that unsupported format raises ValueError."""
        with tempfile.NamedTemporaryFile(suffix=".unsupported", delete=False) as f:
            temp_path = Path(f.name)

        try:
            with pytest.raises(ValueError, match="Unsupported output format"):
                write_output_file(sample_dataframe, temp_path)
        finally:
            temp_path.unlink()

    def test_write_with_string_path(self, sample_dataframe):
        """Test writing using string path instead of Path object."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_path = f.name

        try:
            write_output_file(sample_dataframe, temp_path)
            df = pd.read_csv(temp_path)
            pd.testing.assert_frame_equal(df, sample_dataframe)
        finally:
            Path(temp_path).unlink()


class TestRoundTrip:
    """Test reading and writing files in sequence."""

    def test_csv_round_trip(self, sample_dataframe):
        """Test writing then reading a CSV file."""
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_path = Path(f.name)

        try:
            write_output_file(sample_dataframe, temp_path)
            df = read_input_file(temp_path)
            pd.testing.assert_frame_equal(df, sample_dataframe)
        finally:
            temp_path.unlink()

    @pytest.mark.skipif(not HAS_PARQUET, reason="pyarrow or fastparquet not installed")
    def test_parquet_round_trip(self, sample_dataframe):
        """Test writing then reading a Parquet file."""
        with tempfile.NamedTemporaryFile(suffix=".parquet", delete=False) as f:
            temp_path = Path(f.name)

        try:
            write_output_file(sample_dataframe, temp_path)
            df = read_input_file(temp_path)
            pd.testing.assert_frame_equal(df, sample_dataframe)
        finally:
            temp_path.unlink()
