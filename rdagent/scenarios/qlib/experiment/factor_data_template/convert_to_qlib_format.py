#!/usr/bin/env python
"""
Convert crypto H5 data to Qlib native format (calendars/ + features/ + instruments/).

Qlib 0.9.7 cn_data directory structure:
    cn_data/
      calendars/
        day.txt                         # All trading days, one per line (YYYY-MM-DD)
      features/
        <lowercase_instrument>/         # e.g. btcusdt/
          close.day.bin                 # Format: [int32 start_index] + [float32 values...]
          open.day.bin
          high.day.bin
          low.day.bin
          volume.day.bin
          factor.day.bin                # All 1.0 for crypto
      instruments/
        all.txt                         # Tab-separated, NO header: symbol\tstart_date\tend_date

Usage:
    python convert_to_qlib_format.py --h5 daily_pv_all.h5 --output ~/.qlib/qlib_data/cn_data
    python convert_to_qlib_format.py --h5 daily_pv_all.h5 --output ~/.qlib/qlib_data/crypto_data
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# Field name mapping: H5 column -> Qlib feature file basename (lowercase, no $)
FIELD_MAP = {
    "$open": "open",
    "$close": "close",
    "$high": "high",
    "$low": "low",
    "$volume": "volume",
    "$factor": "factor",
}

FREQ = "day"  # Daily frequency suffix in .bin filenames


def convert_h5_to_qlib(h5_path: str, output_dir: str):
    """Convert H5 MultiIndex DataFrame to Qlib native bin format."""
    output_path = Path(output_dir)

    # 1. Read H5
    print(f"[INFO] Reading H5: {h5_path}")
    df = pd.read_hdf(h5_path, key="data")
    print(f"  Shape: {df.shape}")
    print(f"  Index: {df.index.names}")
    print(f"  Columns: {list(df.columns)}")

    # 2. Extract dates and instruments
    dates = sorted(df.index.get_level_values("datetime").unique())
    instruments = sorted(df.index.get_level_values("instrument").unique())

    date_strs = [d.strftime("%Y-%m-%d") if hasattr(d, 'strftime') else str(d)[:10] for d in dates]
    print(f"  Dates: {date_strs[0]} ~ {date_strs[-1]} ({len(dates)} days)")
    print(f"  Instruments: {len(instruments)}")

    # 3. Create directories
    calendars_dir = output_path / "calendars"
    features_dir = output_path / "features"
    instruments_dir = output_path / "instruments"

    calendars_dir.mkdir(parents=True, exist_ok=True)
    features_dir.mkdir(parents=True, exist_ok=True)
    instruments_dir.mkdir(parents=True, exist_ok=True)

    # 4. Write calendars/day.txt
    cal_path = calendars_dir / "day.txt"
    with open(cal_path, "w") as f:
        for ds in date_strs:
            f.write(ds + "\n")
    print(f"  [OK] calendars/day.txt ({len(date_strs)} days)")

    # 5. Write instruments/all.txt (TAB-separated, NO header)
    inst_path = instruments_dir / "all.txt"
    with open(inst_path, "w") as f:
        for inst in instruments:
            inst_str = str(inst)
            inst_df = df.xs(inst_str, level="instrument")
            inst_dates = inst_df.index
            start = inst_dates[0].strftime("%Y-%m-%d") if hasattr(inst_dates[0], 'strftime') else str(inst_dates[0])[:10]
            end = inst_dates[-1].strftime("%Y-%m-%d") if hasattr(inst_dates[-1], 'strftime') else str(inst_dates[-1])[:10]
            f.write(f"{inst_str.lower()}\t{start}\t{end}\n")
    print(f"  [OK] instruments/all.txt ({len(instruments)} instruments, tab-separated)")

    # 6. Build date index lookup
    date_to_idx = {d: i for i, d in enumerate(date_strs)}
    n_dates = len(dates)

    # 7. Write feature .bin files for each instrument
    # Qlib format: [int32 start_index] + [float32 values for each date from start_index]
    h5_columns = [c for c in df.columns]  # e.g., $open, $close, ...

    for inst in instruments:
        inst_str = str(inst).lower()
        inst_dir = features_dir / inst_str
        inst_dir.mkdir(parents=True, exist_ok=True)
        inst_data = df.xs(str(inst), level="instrument")

        for h5_col in h5_columns:
            qlib_name = FIELD_MAP.get(h5_col, h5_col.lower().lstrip("$"))
            bin_path = inst_dir / f"{qlib_name}.{FREQ}.bin"

            # Build float32 array in calendar order (NaN for dates without data)
            arr = np.full(n_dates, np.nan, dtype=np.float32)
            inst_date_strs = [d.strftime("%Y-%m-%d") if hasattr(d, 'strftime') else str(d)[:10] for d in inst_data.index]
            for i, ds in enumerate(inst_date_strs):
                if ds in date_to_idx:
                    arr[date_to_idx[ds]] = float(inst_data.iloc[i][h5_col])

            # Write binary: [int32 start_index] + [float32 values...]
            with open(bin_path, "wb") as f:
                np.hstack([0, arr]).astype(np.float32).tofile(f)

        if inst == instruments[0]:
            # Verify first instrument
            first_file = inst_dir / f"close.{FREQ}.bin"
            data_read = np.fromfile(first_file, dtype=np.float32)
            print(f"  Verified {inst_str}/close.day.bin: {len(data_read)} float32 values "
                  f"(header={data_read[0]}, first_close={data_read[1]:.2f})")

    print(f"\n[SUCCESS] Qlib data created at: {output_path}")
    print(f"  calendars/day.txt: {len(date_strs)} days")
    print(f"  instruments/all.txt: {len(instruments)} instruments (tab-sep, no header)")
    print(f"  features/: {len(instruments)} instruments x {len(h5_columns)} features")
    print(f"    (format: float32, [start_index] + [values...], file: {{field}}.{FREQ}.bin)")


def main():
    parser = argparse.ArgumentParser(description="Convert crypto H5 to Qlib native format (0.9.7)")
    parser.add_argument("--h5", default=None, help="Path to daily_pv_all.h5 (default: auto-detect)")
    parser.add_argument("--output", default=None, help="Output directory (default: ~/.qlib/qlib_data/cn_data)")
    args = parser.parse_args()

    if args.h5 is None:
        for _name in ["daily_pv_all.h5", "daily_pv_debug.h5"]:
            _candidate = Path(__file__).parent / _name
            if _candidate.exists():
                h5_path = _candidate
                break
        else:
            print("[ERROR] H5 file not found. Specify with --h5 or run generate_crypto.py first.")
            sys.exit(1)
    else:
        h5_path = Path(args.h5)

    if not h5_path.exists():
        print(f"[ERROR] H5 file not found: {h5_path}")
        sys.exit(1)

    output_dir = Path(args.output) if args.output else Path.home() / ".qlib" / "qlib_data" / "cn_data"
    convert_h5_to_qlib(str(h5_path), str(output_dir))


if __name__ == "__main__":
    main()
