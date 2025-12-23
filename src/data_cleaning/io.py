from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd


InputFormat = Literal["csv", "xlsx", "xls", "parquet"]


def read_input_file(path: str | Path, *, fmt: InputFormat | None = None, **kwargs) -> pd.DataFrame:
    """
    Read a file into a DataFrame.

    Supported formats: csv, xlsx/xls, parquet.
    - `fmt`: override inferred format (by suffix).
    - `kwargs`: forwarded to the underlying pandas reader.
    """
    p = Path(path)
    inferred = p.suffix.lower().lstrip(".")
    fmt = (fmt or inferred)  # type: ignore[assignment]

    if fmt == "csv":
        return pd.read_csv(p, **kwargs)
    if fmt in ("xlsx", "xls"):
        return pd.read_excel(p, **kwargs)
    if fmt == "parquet":
        return pd.read_parquet(p, **kwargs)

    raise ValueError(
        f"Unsupported input format '{fmt}'. Supported: csv, xlsx/xls, parquet."
    )


def write_output_file(
    df: pd.DataFrame,
    path: str | Path,
    *,
    fmt: InputFormat | None = None,
    index: bool = False,
    **kwargs,
) -> None:
    """
    Write a DataFrame to a file.

    Supported formats: csv, xlsx/xls, parquet.
    - `fmt`: override inferred format (by suffix).
    - `index`: include DataFrame index (defaults False).
    - `kwargs`: forwarded to the underlying pandas writer.
    """
    p = Path(path)
    inferred = p.suffix.lower().lstrip(".")
    fmt = (fmt or inferred)  # type: ignore[assignment]

    if fmt == "csv":
        df.to_csv(p, index=index, **kwargs)
        return
    if fmt in ("xlsx", "xls"):
        df.to_excel(p, index=index, **kwargs)
        return
    if fmt == "parquet":
        df.to_parquet(p, index=index, **kwargs)
        return

    raise ValueError(
        f"Unsupported output format '{fmt}'. Supported: csv, xlsx/xls, parquet."
    )

