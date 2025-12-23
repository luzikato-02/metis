# Data Cleaning Application - User Guide

A Python application for cleaning and preparing production data for analysis. This guide covers all usage scenarios from basic CLI commands to advanced library integration.

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [CLI Usage](#cli-usage)
4. [Library Usage](#library-usage)
5. [Configuration Options](#configuration-options)
6. [Input/Output Formats](#inputoutput-formats)
7. [Data Cleaning Pipeline](#data-cleaning-pipeline)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)

---

## Installation

### Option 1: Install as Package (Recommended)

```bash
# Clone or download the project
cd /path/to/data-cleaning

# Install with pip (includes CLI command)
python -m pip install -e .

# Install with development dependencies (includes pytest)
python -m pip install -e ".[dev]"
```

After installation, the `data-clean` command will be available globally.

### Option 2: Run Without Installation

You can run the application directly using `main.py`:

```bash
python main.py input.csv output.csv
```

### Dependencies

- **Required**: `pandas >= 2.2.0`
- **Optional**: `pyarrow` or `fastparquet` (for Parquet file support)
- **Optional**: `openpyxl` (for Excel file support)
- **Development**: `pytest >= 8.0.0`

---

## Quick Start

### Basic Usage

```bash
# Clean a CSV file with default settings
data-clean input.csv cleaned.csv

# Or without installation
python main.py input.csv cleaned.csv
```

### Python Library

```python
import pandas as pd
from data_cleaning import DataCleaner, DataCleaningConfig

# Load your data
df_raw = pd.read_csv("input.csv")

# Clean with default settings
df_clean = DataCleaner().clean(df_raw)

# Or with custom configuration
cfg = DataCleaningConfig(rpm_max=9000, efficiency_min=70)
df_clean = DataCleaner(cfg).clean(df_raw)
```

---

## CLI Usage

### Command Syntax

```bash
data-clean INPUT OUTPUT [OPTIONS]
```

### Positional Arguments

| Argument | Description |
|----------|-------------|
| `INPUT`  | Path to input file (.csv, .xlsx, .xls, or .parquet) |
| `OUTPUT` | Path to output file (.csv, .xlsx, .xls, or .parquet) |

### Optional Arguments

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--rpm-max` | float | 10000 | Maximum RPM threshold (rows above are filtered) |
| `--eff-min` | float | 75.0 | Minimum machine efficiency percentage |
| `--eff-max` | float | 100.0 | Maximum machine efficiency percentage |
| `--spindles` | int | 84 | Number of spindles per machine side |
| `--shift-hours` | float | 8.0 | Duration of a shift in hours |
| `--keep-multi-style-shifts` | flag | False | Keep shifts where multiple styles ran on same (date, shift, machine) |
| `--input-format` | string | auto | Override input format detection (csv/xlsx/xls/parquet) |
| `--output-format` | string | auto | Override output format detection (csv/xlsx/xls/parquet) |

### CLI Examples

```bash
# Basic cleaning
data-clean production_data.csv cleaned_data.csv

# Custom RPM and efficiency thresholds
data-clean input.csv output.csv --rpm-max 9000 --eff-min 70 --eff-max 100

# 12-hour shifts with 100 spindles
data-clean input.csv output.csv --shift-hours 12 --spindles 100

# Keep multi-style shifts (don't filter them out)
data-clean input.csv output.csv --keep-multi-style-shifts

# Force format detection for non-standard extensions
data-clean input.data cleaned.out --input-format csv --output-format csv

# Convert CSV to Parquet while cleaning
data-clean input.csv output.parquet

# Full example with all options
data-clean raw_data.csv clean_data.csv \
    --rpm-max 9000 \
    --eff-min 70 \
    --eff-max 100 \
    --spindles 84 \
    --shift-hours 8 \
    --keep-multi-style-shifts
```

---

## Library Usage

### Basic Usage

```python
from data_cleaning import DataCleaner, DataCleaningConfig

# Create cleaner with default config
cleaner = DataCleaner()

# Clean a DataFrame
df_clean = cleaner.clean(df_raw)
```

### Custom Configuration

```python
from data_cleaning import DataCleaner, DataCleaningConfig

# Create custom configuration
cfg = DataCleaningConfig(
    rpm_max=9000,              # Max RPM threshold
    efficiency_min=70.0,       # Min efficiency %
    efficiency_max=100.0,      # Max efficiency %
    spindles_per_side=100,     # Spindles per machine
    shift_hours=12.0,          # Shift duration
    drop_multi_style_shifts=False,  # Keep multi-style shifts
)

# Create cleaner with custom config
cleaner = DataCleaner(config=cfg)
df_clean = cleaner.clean(df_raw)
```

### Using the High-Level Job Runner

```python
from data_cleaning import run_cleaning_job, DataCleaningConfig

# Simple job
run_cleaning_job("input.csv", "output.csv")

# With custom config
cfg = DataCleaningConfig(rpm_max=9000)
run_cleaning_job(
    "input.csv",
    "output.csv",
    config=cfg,
    input_format="csv",   # Optional: override format
    output_format="csv",  # Optional: override format
)
```

### File I/O Functions

```python
from data_cleaning import read_input_file, write_output_file

# Read files
df = read_input_file("data.csv")
df = read_input_file("data.xlsx")
df = read_input_file("data.parquet")

# Read with format override
df = read_input_file("data.txt", fmt="csv")

# Write files
write_output_file(df, "output.csv")
write_output_file(df, "output.xlsx")
write_output_file(df, "output.parquet")

# Write with index
write_output_file(df, "output.csv", index=True)

# Write with format override
write_output_file(df, "output.txt", fmt="csv")
```

### Accessing the Configuration

```python
from data_cleaning import DataCleaningConfig

# Create config and inspect defaults
cfg = DataCleaningConfig()

print(cfg.rpm_max)           # 10000
print(cfg.efficiency_min)    # 75.0
print(cfg.efficiency_max)    # 100.0
print(cfg.spindles_per_side) # 84
print(cfg.shift_hours)       # 8.0

# Column name configuration
print(cfg.col_date)          # "Date"
print(cfg.col_shift)         # "Shift_period"
print(cfg.col_machine)       # "Machine-number"
print(cfg.col_style)         # "Style-description"
print(cfg.col_runtime)       # "Run_time"
print(cfg.col_rpm)           # "RPM"

# Rename map for embedded newlines in headers
print(cfg.rename_map)        # {"Shift\nperiod": "Shift_period", "Run\ntime": "Run_time"}
```

---

## Configuration Options

### DataCleaningConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `rpm_max` | float | 10000 | Maximum RPM value; rows with higher RPM are filtered out |
| `efficiency_min` | float | 75.0 | Minimum machine efficiency percentage to keep |
| `efficiency_max` | float | 100.0 | Maximum machine efficiency percentage to keep |
| `spindles_per_side` | int | 84 | Number of spindles per machine side (used in efficiency calculation) |
| `shift_hours` | float | 8.0 | Duration of a shift in hours (used in efficiency calculation) |
| `drop_multi_style_shifts` | bool | True | Whether to drop shifts with multiple styles on same (date, shift, machine) |
| `col_date` | str | "Date" | Column name for date |
| `col_shift` | str | "Shift_period" | Column name for shift period |
| `col_machine` | str | "Machine-number" | Column name for machine number |
| `col_style` | str | "Style-description" | Column name for style description |
| `col_runtime` | str | "Run_time" | Column name for run time |
| `col_rpm` | str | "RPM" | Column name for RPM |
| `rename_map` | dict | (auto) | Column rename mapping (handles embedded newlines) |

### Custom Column Names

If your data uses different column names:

```python
cfg = DataCleaningConfig(
    col_date="ProductionDate",
    col_shift="ShiftType",
    col_machine="MachineID",
    col_style="ProductStyle",
    col_runtime="TotalRunTime",
    col_rpm="SpindleRPM",
)
```

---

## Input/Output Formats

### Supported Formats

| Format | Extensions | Read | Write | Requirements |
|--------|------------|------|-------|--------------|
| CSV | `.csv` | ✅ | ✅ | pandas (included) |
| Excel | `.xlsx`, `.xls` | ✅ | ✅ | openpyxl |
| Parquet | `.parquet` | ✅ | ✅ | pyarrow or fastparquet |

### Format Detection

The format is automatically detected from the file extension. Use `--input-format` and `--output-format` (CLI) or `fmt` parameter (library) to override.

### Installing Optional Dependencies

```bash
# For Excel support
pip install openpyxl

# For Parquet support (choose one)
pip install pyarrow
# or
pip install fastparquet
```

---

## Data Cleaning Pipeline

The `DataCleaner.clean()` method performs these steps in order:

### 1. Column Renaming
Renames columns with embedded newlines (e.g., `"Shift\nperiod"` → `"Shift_period"`).

### 2. Required Column Validation
Verifies these columns exist (after renaming):
- `Date`
- `Shift_period`
- `Machine-number`
- `Style-description`
- `Run_time`
- `RPM`

### 3. Type Coercion
- `Date` → datetime
- `RPM` → numeric
- `Run_time` → timedelta → `Run_time_seconds` (float)

### 4. Drop Invalid Rows
Rows with invalid/missing Date, RPM, or Run_time are removed.

### 5. RPM Filter
Rows where `RPM > rpm_max` are removed.

### 6. Multi-Style Shift Filter (Optional)
If `drop_multi_style_shifts=True`, removes all rows from (Date, Shift, Machine) groups where more than one style was produced.

### 7. Derived Metrics Calculation
New columns are added:
- `Run_time_seconds`: Total runtime in seconds
- `Run_time_per_spindle_seconds`: Runtime divided by number of spindles
- `Run_time_per_spindle_hours`: Runtime per spindle in hours
- `Machine_Efficiency`: `(Run_time_seconds / (shift_hours * 3600 * spindles)) * 100`

### 8. Efficiency Filter
Rows where `Machine_Efficiency` is outside `[efficiency_min, efficiency_max]` are removed.

---

## Examples

### Example 1: Basic Production Data Cleaning

```python
import pandas as pd
from data_cleaning import DataCleaner, DataCleaningConfig

# Sample production data
data = {
    "Date": ["2024-01-15", "2024-01-15", "2024-01-16"],
    "Shift_period": ["Day", "Night", "Day"],
    "Machine-number": ["M001", "M001", "M002"],
    "Style-description": ["Style-A", "Style-A", "Style-B"],
    "Run_time": ["07:30:00", "06:45:00", "08:00:00"],
    "RPM": [5500, 6000, 5800],
}
df_raw = pd.DataFrame(data)

# Clean with relaxed efficiency filter
cfg = DataCleaningConfig(efficiency_min=0, efficiency_max=100)
cleaner = DataCleaner(config=cfg)
df_clean = cleaner.clean(df_raw)

print(df_clean[["Date", "Machine-number", "RPM", "Machine_Efficiency"]])
```

### Example 2: Batch Processing Multiple Files

```python
from pathlib import Path
from data_cleaning import run_cleaning_job, DataCleaningConfig

# Configuration for all files
cfg = DataCleaningConfig(
    rpm_max=9000,
    efficiency_min=70,
    efficiency_max=100,
)

# Process all CSV files in a directory
input_dir = Path("raw_data")
output_dir = Path("cleaned_data")
output_dir.mkdir(exist_ok=True)

for input_file in input_dir.glob("*.csv"):
    output_file = output_dir / f"cleaned_{input_file.name}"
    run_cleaning_job(input_file, output_file, config=cfg)
    print(f"Processed: {input_file.name}")
```

### Example 3: Data Analysis After Cleaning

```python
import pandas as pd
from data_cleaning import DataCleaner, DataCleaningConfig

# Load and clean data
df_raw = pd.read_csv("production_data.csv")
cfg = DataCleaningConfig(efficiency_min=0)
df = DataCleaner(cfg).clean(df_raw)

# Analysis: Average efficiency by machine
efficiency_by_machine = df.groupby("Machine-number")["Machine_Efficiency"].mean()
print("Average Efficiency by Machine:")
print(efficiency_by_machine.sort_values(ascending=False))

# Analysis: Daily production summary
daily_summary = df.groupby("Date").agg({
    "Run_time_seconds": "sum",
    "Machine_Efficiency": "mean",
    "RPM": "mean",
})
print("\nDaily Summary:")
print(daily_summary)
```

### Example 4: Custom Column Names

```python
from data_cleaning import DataCleaner, DataCleaningConfig

# Your data uses different column names
cfg = DataCleaningConfig(
    col_date="production_date",
    col_shift="shift_type",
    col_machine="machine_id",
    col_style="product_style",
    col_runtime="total_runtime",
    col_rpm="spindle_rpm",
    efficiency_min=0,
)

cleaner = DataCleaner(config=cfg)
df_clean = cleaner.clean(df_raw)
```

---

## Troubleshooting

### Common Issues

#### "Missing required columns" Error

**Cause**: Your input data doesn't have the expected column names.

**Solution**: Either rename your columns to match the defaults, or configure custom column names:

```python
cfg = DataCleaningConfig(
    col_date="YourDateColumn",
    col_shift="YourShiftColumn",
    # ... etc
)
```

#### All Rows Filtered Out

**Cause**: The efficiency filter is too strict for your data.

**Solution**: Check your data's actual efficiency values and adjust the thresholds:

```python
# First, check what efficiency values you have
cfg = DataCleaningConfig(efficiency_min=0, efficiency_max=1000)
df = DataCleaner(cfg).clean(df_raw)
print(df["Machine_Efficiency"].describe())

# Then set appropriate thresholds
cfg = DataCleaningConfig(efficiency_min=0, efficiency_max=100)
```

#### "Unsupported input format" Error

**Cause**: File extension not recognized.

**Solution**: Use format override:

```bash
data-clean input.txt output.txt --input-format csv --output-format csv
```

#### Parquet Files Not Working

**Cause**: Missing parquet library.

**Solution**: Install pyarrow:

```bash
pip install pyarrow
```

#### Excel Files Not Working

**Cause**: Missing openpyxl library.

**Solution**: Install openpyxl:

```bash
pip install openpyxl
```

### Getting Help

```bash
# View CLI help
data-clean --help
```

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_cleaner.py -v
```

---

## API Reference

### Public API (from `data_cleaning`)

| Export | Type | Description |
|--------|------|-------------|
| `DataCleaner` | class | Main cleaner class with `clean(df)` method |
| `DataCleaningConfig` | dataclass | Configuration container |
| `read_input_file` | function | Read CSV/Excel/Parquet files |
| `write_output_file` | function | Write CSV/Excel/Parquet files |
| `run_cleaning_job` | function | High-level: read → clean → write |

### DataCleaner Methods

| Method | Arguments | Returns | Description |
|--------|-----------|---------|-------------|
| `__init__` | `config: DataCleaningConfig \| None` | None | Initialize with optional config |
| `clean` | `df_raw: pd.DataFrame` | `pd.DataFrame` | Clean the input DataFrame |

---

## Version Information

- **Package**: data-cleaning v0.1.0
- **Python**: >= 3.10
- **Pandas**: >= 2.2.0
