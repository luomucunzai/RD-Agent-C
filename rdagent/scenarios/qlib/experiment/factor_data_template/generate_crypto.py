#!/usr/bin/env python
"""
Generate daily_pv.h5 from Binance CSV data (downdata.py output).
No $factor column — cryptocurrency has no adjustment factor.

Usage:
    python generate_crypto.py                    # Uses CSV from ../binance_futures_data/
    python generate_crypto.py --debug            # Generates debug version (subset)

Output:
    daily_pv.h5  (or daily_pv_debug.h5) with MultiIndex (datetime, instrument)
    Columns: $open, $close, $high, $low, $volume, $factor
    $factor=1.0 always (crypto has no adjustment, factor=1 = no adjustment)
"""

import argparse
import sys
from pathlib import Path

import pandas as pd


def load_binance_csv(csv_path: str) -> pd.DataFrame | None:
    """Load a Binance CSV and return a DataFrame with datetime index and OHLCV columns."""
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"  [SKIP] {csv_path} not found")
        return None
    except pd.errors.EmptyDataError:
        print(f"  [SKIP] {csv_path} is empty")
        return None

    # Map Binance column names to standard format
    # Binance CSV columns: open_time, open, high, low, close, volume, ...
    time_col = None
    for candidate in ["open_time", "timestamp", "date", "datetime"]:
        if candidate in df.columns:
            time_col = candidate
            break

    if time_col is None:
        print(f"  [SKIP] {csv_path}: no time column found (columns: {list(df.columns)})")
        return None

    # Convert time to datetime
    if df[time_col].dtype == "object":
        df[time_col] = pd.to_datetime(df[time_col])
    else:
        # Unix timestamp in ms
        df[time_col] = pd.to_datetime(df[time_col], unit="ms")

    # Make a local time column (normalize to date for daily frequency)
    df["_date"] = df[time_col].dt.tz_localize(None).dt.normalize()

    # Remove duplicates and sort
    df = df.drop_duplicates(subset=["_date"]).sort_values("_date")

    # Extract symbol from filename
    symbol = Path(csv_path).stem

    # Build result with standard column names
    result = pd.DataFrame({
        "datetime": df["_date"].values,
        "$open": pd.to_numeric(df["open"].values, errors="coerce"),
        "$close": pd.to_numeric(df["close"].values, errors="coerce"),
        "$high": pd.to_numeric(df["high"].values, errors="coerce"),
        "$low": pd.to_numeric(df["low"].values, errors="coerce"),
        "$volume": pd.to_numeric(df["volume"].values, errors="coerce"),
        "$factor": 1.0,  # Cryptocurrency has no adjustment factor; factor=1 means no adjustment needed
        "instrument": symbol,
    })

    return result.set_index(["datetime", "instrument"]).sort_index()


def main():
    parser = argparse.ArgumentParser(description="Generate crypto H5 data from Binance CSV")
    parser.add_argument("--debug", action="store_true", help="Generate debug version (subset)")
    args = parser.parse_args()

    # Input: CSV directory (from downdata.py)
    script_dir = Path(__file__).parent
    csv_dir = script_dir.parent.parent.parent.parent.parent / "binance_futures_data"
    # Also check relative path from project root
    alt_csv_dir = Path.cwd() / "binance_futures_data"

    if csv_dir.exists():
        data_dir = csv_dir
    elif alt_csv_dir.exists():
        data_dir = alt_csv_dir
    else:
        print(f"[ERROR] Binance data directory not found.")
        print(f"  Tried: {csv_dir}")
        print(f"  Tried: {alt_csv_dir}")
        print(f"  Please run downdata.py first to download cryptocurrency data.")
        sys.exit(1)

    csv_files = sorted(data_dir.glob("*.csv"))
    if not csv_files:
        print(f"[ERROR] No CSV files found in {data_dir}")
        sys.exit(1)

    print(f"[INFO] Found {len(csv_files)} CSV files in {data_dir}")

    all_dfs = []
    for csv_path in csv_files:
        symbol = csv_path.stem
        print(f"  Processing {symbol}...")
        df = load_binance_csv(str(csv_path))
        if df is not None:
            all_dfs.append(df)
            print(f"    -> {len(df)} rows, {df.index.get_level_values('datetime').min().date()} to {df.index.get_level_values('datetime').max().date()}")

    if not all_dfs:
        print("[ERROR] No valid data loaded.")
        sys.exit(1)

    # Combine all symbols into one MultiIndex DataFrame
    combined = pd.concat(all_dfs, axis=0)
    combined = combined.sort_index()

    # Remove any rows where all OHLCV is NaN
    combined = combined.dropna(how="all", subset=["$open", "$close", "$high", "$low", "$volume"])

    print(f"\n[INFO] Combined data: {len(combined)} rows, {len(combined.index.get_level_values('instrument').unique())} instruments")
    print(f"[INFO] Date range: {combined.index.get_level_values('datetime').min().date()} to {combined.index.get_level_values('datetime').max().date()}")
    print(f"[INFO] Columns: {list(combined.columns)}")
    assert "$factor" in combined.columns, "ERROR: $factor column is required for Qlib compatibility!"
    assert combined["$factor"].unique().tolist() == [1.0], "ERROR: $factor should all be 1.0 for crypto!"

    # Output path
    if args.debug:
        # Debug: use first 2 instruments, recent 1 year
        instruments = combined.index.get_level_values("instrument").unique()[:2]
        debug_data = combined.loc[combined.index.get_level_values("instrument").isin(instruments)]
        # Filter to last year
        last_year = pd.Timestamp.now() - pd.DateOffset(years=1)
        debug_data = debug_data.loc[debug_data.index.get_level_values("datetime") >= last_year]
        output_path = script_dir / "daily_pv_debug.h5"
        debug_data.to_hdf(output_path, key="data")
        print(f"\n[SUCCESS] Debug data saved to {output_path}")
        print(f"  Instruments: {list(instruments)}")
        print(f"  Rows: {len(debug_data)}")
    else:
        output_path = script_dir / "daily_pv_all.h5"
        combined.to_hdf(output_path, key="data")
        print(f"\n[SUCCESS] Full data saved to {output_path}")
        print(f"  Instruments: {len(combined.index.get_level_values('instrument').unique())}")
        print(f"  Rows: {len(combined)}")

    # Also generate README.md for crypto data
    readme_path = script_dir / "README.md"
    # Keep existing README content but ensure it reflects crypto data
    print(f"[INFO] Using existing README.md (already updated for CRYPTO_MODE)")


if __name__ == "__main__":
    main()
