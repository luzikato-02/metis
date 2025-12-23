from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DataCleaningConfig:
    rpm_max: float = 10_000
    efficiency_min: float = 75.0
    efficiency_max: float = 100.0
    spindles_per_side: int = 84
    shift_hours: float = 8.0
    drop_multi_style_shifts: bool = True

    # Column names (post-rename)
    col_date: str = "Date"
    col_shift: str = "Shift_period"
    col_machine: str = "Machine-number"
    col_style: str = "Style-description"
    col_runtime: str = "Run_time"
    col_rpm: str = "RPM"

    # Rename map (raw -> cleaned). Supports embedded newlines in headers.
    rename_map: dict[str, str] | None = None

    def __post_init__(self) -> None:
        # dataclass(frozen=True) requires object.__setattr__
        object.__setattr__(
            self,
            "rename_map",
            {
                "Shift\nperiod": "Shift_period",
                "Run\ntime": "Run_time",
            },
        )

