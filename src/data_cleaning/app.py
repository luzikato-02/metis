from __future__ import annotations

from pathlib import Path

from .cleaner import DataCleaner
from .config import DataCleaningConfig
from .io import read_input_file, write_output_file


def run_cleaning_job(
    input_path: str | Path,
    output_path: str | Path,
    *,
    config: DataCleaningConfig | None = None,
    input_format: str | None = None,
    output_format: str | None = None,
) -> None:
    """
    Main "app" function: read file -> clean -> write file.
    """
    df_raw = read_input_file(input_path, fmt=input_format)  # type: ignore[arg-type]
    cleaner = DataCleaner(config=config)
    df_clean = cleaner.clean(df_raw)
    write_output_file(df_clean, output_path, fmt=output_format)  # type: ignore[arg-type]

