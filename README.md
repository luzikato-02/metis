# data-cleaning

Small Python project that cleans production data for analysis using an OOP cleaner (`DataCleaner`).

## Install (recommended)

```bash
python -m pip install -e ".[dev]"
```

## Run (CLI)

```bash
data-clean input.csv cleaned.csv
```

Common options:

```bash
data-clean input.csv cleaned.csv --rpm-max 9000 --eff-min 70 --eff-max 100 --shift-hours 8 --spindles 84
```

If your file extension is unusual, you can force formats:

```bash
data-clean input.data cleaned.out --input-format csv --output-format csv
```

## Run (without install)

```bash
python main.py input.csv cleaned.csv
```

## Use as a library

```python
import pandas as pd
from data_cleaning import DataCleaner, DataCleaningConfig

df_raw = pd.read_csv("input.csv")
cfg = DataCleaningConfig(rpm_max=10_000, efficiency_min=75, efficiency_max=100)
df_clean = DataCleaner(cfg).clean(df_raw)
```