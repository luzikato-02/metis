from __future__ import annotations

import pandas as pd

from .config import DataCleaningConfig


class DataCleaner:
    def __init__(self, config: DataCleaningConfig | None = None):
        self.config = config or DataCleaningConfig()

    def clean(self, df_raw: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and prepare production data for analysis.

        Returns a new DataFrame (does not mutate the input).
        """
        df = df_raw.copy()

        # 1) Rename columns (handles embedded newlines)
        df = df.rename(columns=self.config.rename_map or {})

        # 2) Validate required columns exist
        required = {
            self.config.col_date,
            self.config.col_shift,
            self.config.col_machine,
            self.config.col_style,
            self.config.col_runtime,
            self.config.col_rpm,
        }
        missing = required - set(df.columns)
        if missing:
            raise KeyError(f"Missing required columns: {sorted(missing)}")

        # 3) Coerce types
        df[self.config.col_date] = pd.to_datetime(df[self.config.col_date], errors="coerce")
        df[self.config.col_rpm] = pd.to_numeric(df[self.config.col_rpm], errors="coerce")

        run_td = pd.to_timedelta(df[self.config.col_runtime].astype("string"), errors="coerce")
        df["Run_time_seconds"] = run_td.dt.total_seconds()

        # Drop unusable rows
        df = df.dropna(subset=[self.config.col_date, self.config.col_rpm, "Run_time_seconds"])

        # 4) Filter RPM outliers
        df = df.loc[df[self.config.col_rpm] <= self.config.rpm_max].copy()

        # 5) Optionally remove multi-style (Date, Shift, Machine) groups
        if self.config.drop_multi_style_shifts:
            keys = [self.config.col_date, self.config.col_shift, self.config.col_machine]
            style_counts = df.groupby(keys, dropna=False)[self.config.col_style].nunique()
            bad_keys = style_counts[style_counts > 1].index
            df = df.loc[~df.set_index(keys).index.isin(bad_keys)].copy()

        # 6) Derived metrics
        total_shift_seconds = float(self.config.shift_hours) * 3600.0
        spindles = float(self.config.spindles_per_side)

        df["Run_time_per_spindle_seconds"] = df["Run_time_seconds"] / spindles
        df["Run_time_per_spindle_hours"] = df["Run_time_per_spindle_seconds"] / 3600.0
        df["Machine_Efficiency"] = (
            df["Run_time_seconds"] / (total_shift_seconds * spindles) * 100.0
        )

        # 7) Efficiency range filter
        df = df.loc[
            df["Machine_Efficiency"].between(
                self.config.efficiency_min, self.config.efficiency_max
            )
        ].copy()

        return df

