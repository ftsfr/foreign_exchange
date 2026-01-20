"""
Create FTSFR standardized datasets for foreign exchange returns.

Outputs:
- ftsfr_fx_returns.parquet: Daily FX returns for USD invested in foreign currencies
"""

import sys
from pathlib import Path

sys.path.insert(0, "./src")

import pandas as pd

import chartbook
import calc_fx

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print(">> Creating ftsfr_fx_returns...")
    df_all = calc_fx.calculate_fx(data_dir=DATA_DIR)
    df_all.columns = ["unique_id", "ds", "y"]
    df_all["ds"] = pd.to_datetime(df_all["ds"])

    df_all = df_all.dropna()
    df_all = df_all.sort_values(by=["unique_id", "ds"]).reset_index(drop=True)

    output_path = DATA_DIR / "ftsfr_fx_returns.parquet"
    df_all.to_parquet(output_path, index=False)
    print(f"   Saved: {output_path.name}")
    print(f"   Records: {len(df_all):,}")
    print(f"   Currencies: {df_all['unique_id'].nunique()}")


if __name__ == "__main__":
    main()
