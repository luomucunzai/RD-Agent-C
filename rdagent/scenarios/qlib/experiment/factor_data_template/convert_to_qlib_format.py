#!/usr/bin/env python
"""
Convert crypto H5 data to Qlib native format (calendars/ + features/ + instruments/).

Qlib cn_data directory structure:
    cn_data/
      calendars/
        day.txt          # All trading days, one per line (YYYY-MM-DD)
      features/
        <instrument>/    # One directory per instrument
          $open.bin      # Feature binary files (float64, in calendar order)
          $close.bin
          $high.bin
          $low.bin
          $volume.bin
          $factor.bin
      instruments/
        all.txt          # All instrument symbols, one per line

Usage:
    python convert_to_qlib_format.py --h5 daily_pv_all.h5 --output ~/.qlib/qlib_data/crypto_data
    python convert_to_qlib_format.py --h5 daily_pv_all.h5 --output ~/.qlib/qlib_data/cn_data
"""

import argparse
import struct
import sys
from pathlib import Path

import numpy as np
import pandas as pd


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

    # 5. Write instruments/all.txt
    inst_path = instruments_dir / "all.txt"
    with open(inst_path, "w") as f:
        for inst in instruments:
            f.write(str(inst) + "\n")
    print(f"  [OK] instruments/all.txt ({len(instruments)} instruments)")

    # 6. Build date index lookup (date string -> position in calendar)
    date_to_idx = {d: i for i, d in enumerate(date_strs)}
    n_dates = len(dates)

    # 7. Write feature .bin files for each instrument
    magic = 20220926  # Qlib CalMCSingleFileStorage magic number
    feature_columns = [c for c in df.columns]  # e.g., $open, $close, $high, $low, $volume, $factor

    for inst in instruments:
        inst_dir = features_dir / str(inst)
        inst_dir.mkdir(parents=True, exist_ok=True)

        # Get data for this instrument
        inst_data = df.xs(inst, level="instrument")

        for feat in feature_columns:
            bin_path = inst_dir / f"{feat}.bin"

            # Build array in calendar order (NaN for missing dates)
            arr = np.full(n_dates, np.nan, dtype=np.float64)

            # Map available dates to positions
            inst_dates = inst_data.index
            if hasattr(inst_dates, 'strftime'):
                inst_date_strs = [d.strftime("%Y-%m-%d") for d in inst_dates]
            else:
                inst_date_strs = [str(d)[:10] for d in inst_dates]

            for i, ds in enumerate(inst_date_strs):
                if ds in date_to_idx:
                    arr[date_to_idx[ds]] = float(inst_data.iloc[i][feat])

            # Write binary file
            with open(bin_path, "wb") as f:
                f.write(struct.pack("I", magic))        # uint32 magic number
                f.write(struct.pack("I", n_dates))       # uint32 count
                f.write(arr.tobytes())                   # float64 values

            # Verify on first instrument
            if inst == instruments[0]:
                with open(bin_path, "rb") as f:
                    actual_magic = struct.unpack("I", f.read(4))[0]
                    actual_count = struct.unpack("I", f.read(4))[0]
                    actual_data = np.frombuffer(f.read(), dtype=np.float64)
                assert actual_magic == magic, f"Magic mismatch: {actual_magic}"
                assert actual_count == n_dates, f"Count mismatch: {actual_count}"
                print(f"  Verified {inst}/{feat}.bin: magic={actual_magic}, count={actual_count}, "
                      f"valid={np.sum(~np.isnan(actual_data))}")

        if inst == instruments[0]:
            print(f"  [OK] features/{inst}/ (... {len(feature_columns)} features)")

    print(f"\n[SUCCESS] Qlib data created at: {output_path}")
    print(f"  calendars/day.txt: {len(date_strs)} days")
    print(f"  instruments/all.txt: {len(instruments)} instruments")
    print(f"  features/: {len(instruments)} instruments x {len(feature_columns)} features")

    # 8. Print summary
    print(f"\n  Directory structure:")
    print(f"    {output_path}/")
    print(f"    ├── calendars/")
    print(f"    │   └── day.txt  ({len(date_strs)} lines)")
    print(f"    ├── features/")
    for inst in instruments[:3]:
        print(f"    │   ├── {inst}/")
        for feat in feature_columns[:3]:
            print(f"    │   │   ├── {feat}.bin")
        if len(feature_columns) > 3:
            print(f"    │   │   └── ... (total: {len(feature_columns)} features)")
    if len(instruments) > 3:
        print(f"    │   └── ... (total: {len(instruments)} instruments)")
    print(f"    └── instruments/")
    print(f"        └── all.txt  ({len(instruments)} lines)")


def main():
    parser = argparse.ArgumentParser(description="Convert crypto H5 to Qlib native format")
    parser.add_argument("--h5", default=None,
                        help="Path to daily_pv_all.h5 (default: auto-detect)")
    parser.add_argument("--output", default=None,
                        help="Output directory (default: ~/.qlib/qlib_data/cn_data)")
    args = parser.parse_args()

    # Auto-detect H5 path
    if args.h5 is None:
        candidate = Path(__file__).parent / "daily_pv_all.h5"
        if candidate.exists():
            h5_path = candidate
        else:
            print("[ERROR] H5 file not found. Specify with --h5 or run generate_crypto.py first.")
            sys.exit(1)
    else:
        h5_path = Path(args.h5)

    if not h5_path.exists():
        print(f"[ERROR] H5 file not found: {h5_path}")
        sys.exit(1)

    # Default output
    if args.output is None:
        output_dir = Path.home() / ".qlib" / "qlib_data" / "cn_data"
    else:
        output_dir = Path(args.output)

    convert_h5_to_qlib(str(h5_path), str(output_dir))


if __name__ == "__main__":
    main()
