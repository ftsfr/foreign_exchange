"""
Calculate foreign exchange daily returns for USD invested in foreign currencies.

This module implements a strategy where USD is converted to a foreign currency at the
end of day t-1, invested in that currency's overnight repo market, and then converted
back to USD on day t.

The methodology calculates returns as:
    ret_{t,i} = (spot_{t-1,i} / spot_{t,i}) * fret_{t,i}

Where:
    - i is the foreign currency
    - t is the date of the implied foreign currency return
    - ret is the return of USD invested in the foreign currency
    - fret is the return of the foreign currency when invested in their overnight repo market
    - spot is the spot price of the currency (how much 1 USD is worth in the foreign currency)

Data Sources:
    - Bloomberg FX spot rates
    - Bloomberg interest rates (OIS)

Code adapted with permission from https://github.com/Kunj121/CIP
"""

import sys
from pathlib import Path

sys.path.insert(0, "./src")

import pandas as pd
import matplotlib.pyplot as plt

import chartbook
import pull_bbg_foreign_exchange

BASE_DIR = chartbook.env.get_project_root()
DATA_DIR = BASE_DIR / "_data"

CURRENCIES = ["AUD", "CAD", "CHF", "EUR", "GBP", "JPY", "NZD", "SEK", "USD"]


def prepare_fx_data(spot_rates, interest_rates):
    """
    Prepare foreign exchange data for calculations.

    This function:
    1. Sets Date as index for all dataframes
    2. Standardizes column names
    3. Converts certain currencies to reciprocals (EUR, GBP, AUD, NZD)
    4. Merges all data into a single DataFrame
    """
    # Set Date as index
    spot_rates = (
        spot_rates.set_index("index") if "index" in spot_rates.columns else spot_rates
    )
    interest_rates = (
        interest_rates.set_index("index")
        if "index" in interest_rates.columns
        else interest_rates
    )

    # Standard column names for currencies
    cols = ["AUD", "CAD", "CHF", "EUR", "GBP", "JPY", "NZD", "SEK", "USD"]
    int_cols = ["ADS", "CDS", "SFS", "EUS", "BPS", "JYS", "NDS", "SKS", "USS"]

    # Clean up column names - extract currency codes from Bloomberg tickers if needed
    def clean_columns(df, suffix="", interest_rate=False):
        new_cols = []
        for col in df.columns:
            # Extract currency code from Bloomberg ticker format
            if "_PX_LAST" in col:
                currency = col.split()[0][:3]
                new_cols.append(currency)
            else:
                new_cols.append(col)

        df.columns = new_cols
        return df

    # Clean and rename columns
    spot_rates = clean_columns(spot_rates)
    interest_rates = clean_columns(interest_rates, interest_rate=True)

    # Map interest rate columns from int_cols to cols
    ir_mapping = dict(zip(int_cols, cols))
    interest_rates = interest_rates.rename(columns=ir_mapping)

    # Rename columns to keep track
    spot_rates.columns = [f"{name}_spot" for name in spot_rates.columns]
    interest_rates.columns = [f"{name}_ir" for name in interest_rates.columns]

    # Merge all dataframes
    df_merged = spot_rates.merge(
        interest_rates, left_index=True, right_index=True, how="inner"
    )

    # Convert to reciprocal for these currencies (quoted as foreign/USD instead of USD/foreign)
    reciprocal_currencies = ["EUR", "GBP", "AUD", "NZD"]
    for ccy in reciprocal_currencies:
        if f"{ccy}_spot" in df_merged.columns:
            df_merged[f"{ccy}_spot"] = 1.0 / df_merged[f"{ccy}_spot"]

    return df_merged


def implied_daily_fx_returns(fx_data, currency_list):
    """
    Calculate implied daily return time series for USD invested in foreign currencies.

    This function implements the investment strategy where USD is converted to a foreign
    currency, invested in that currency's overnight market, then converted back to USD.
    """
    fx_df = fx_data.copy()
    fx_df = fx_df.ffill()

    # tracking returns columns
    ret_cols = ["USD_return"]

    for curr_name in currency_list:
        int_col = f"{curr_name}_ir"

        if curr_name == "USD":
            fx_df["USD_return"] = fx_df[int_col]
            continue

        spot_col = f"{curr_name}_spot"
        fx_df[f"{spot_col}_ratio"] = fx_df[spot_col].shift(1) / fx_df[spot_col]
        curr_ret_col = f"{curr_name}_return"

        # keep interest conversion consistent with US
        fx_df[curr_ret_col] = fx_df[f"{spot_col}_ratio"] * fx_df[int_col]
        ret_cols.append(curr_ret_col)

    # filter just for returns
    fx_df = fx_df[ret_cols]
    return fx_df


def calculate_fx(end_date="2025-03-01", data_dir=DATA_DIR):
    """
    Calculate foreign exchange daily returns for USD invested in foreign currencies.

    Parameters
    ----------
    end_date : str
        End date for the data
    data_dir : Path, optional
        Directory containing the FX data files.

    Returns
    -------
    pd.DataFrame
        DataFrame with FX returns for each currency in long format
    """
    data_dir = Path(data_dir)
    # Load data
    spot_rates = pull_bbg_foreign_exchange.load_fx_spot_rates(data_dir=data_dir)
    interest_rates = pull_bbg_foreign_exchange.load_fx_interest_rates(data_dir=data_dir)

    # Prepare data
    df_merged = prepare_fx_data(spot_rates, interest_rates)
    # Filter by end date
    if end_date:
        date = pd.Timestamp(end_date).date()
        df_merged = df_merged.loc[:date]

    # Compute FX
    df_merged = implied_daily_fx_returns(df_merged, CURRENCIES)

    # Change things up
    df_merged = df_merged.reset_index().rename(columns={"index": "date"})
    df_long = df_merged.melt(
        id_vars=["date"],
        var_name="currency",
        value_name="returns",
    )
    # specified unique_id, ds, y ordering
    df_long = df_long[["currency", "date", "returns"]]

    return df_long


def load_fx_returns(data_dir=DATA_DIR):
    """Load calculated FX returns from parquet file."""
    path = data_dir / "fx_returns.parquet"
    return pd.read_parquet(path)


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print(">> Calculating FX returns...")
    fx_returns = calculate_fx(data_dir=DATA_DIR)
    print(f">> Records: {len(fx_returns):,}")

    # Save to parquet
    fx_returns.to_parquet(DATA_DIR / "fx_returns.parquet", index=False)
    print(">> Saved fx_returns.parquet")


if __name__ == "__main__":
    main()
