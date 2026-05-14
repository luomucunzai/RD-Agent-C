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
from datetime import timedelta
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

FREQ = "day"  # Always "day" — 1H K线映射为假日期，Qlib 层面仍是日线


def convert_h5_to_qlib(h5_path: str, output_dir: str):
    """Convert H5 MultiIndex DataFrame to Qlib native bin format.

    支持 1H K线：1H 时间戳被映射为连续的假日期（2000-01-01 起）。
    Qlib 层面始终是日线频率，不需要改 freq。
    """
    output_path = Path(output_dir)

    # 1. Read H5
    print(f"[INFO] Reading H5: {h5_path}")
    df = pd.read_hdf(h5_path, key="data")
    print(f"  Shape: {df.shape}")
    print(f"  Index: {df.index.names}")
    print(f"  Columns: {list(df.columns)}")

    # 2. Detect if this is 1H data by checking time spacing
    raw_dates = sorted(df.index.get_level_values("datetime").unique())
    if len(raw_dates) > 1:
        hour_diff = (raw_dates[1] - raw_dates[0]).total_seconds() / 3600
        is_hourly = hour_diff < 12  # 间隔小于12小时 → 是1H数据
    else:
        is_hourly = False

    instruments = sorted(df.index.get_level_values("instrument").unique())
    n_total = len(df)  # 总行数 = 交易对数 × 每个交易对的行数
    rows_per_inst = n_total // len(instruments)

    if is_hourly:
        print(f"  ⏰ 检测到 1H K线数据（{rows_per_inst} 行/交易对），映射为假日期")
        # 每行数据映射到一个假日期：2000-01-01, 2000-01-02, ...
        fake_start = pd.Timestamp("2000-01-01")
        # 重建 DataFrame index: 用 fake date 代替真实时间戳
        # 每个 instrument 的数据保持原有顺序，分配连续的假日期
        new_idx_data = []
        for inst in instruments:
            inst_data = df.xs(str(inst), level="instrument")
            for i in range(len(inst_data)):
                fake_date = fake_start + timedelta(days=i)
                new_idx_data.append((fake_date, str(inst)))
        new_midx = pd.MultiIndex.from_tuples(new_idx_data, names=["datetime", "instrument"])
        df = df.set_index(new_midx)
        df = df.sort_index()

    # 3. Extract dates and instruments
    dates = sorted(df.index.get_level_values("datetime").unique())
    instruments = sorted(df.index.get_level_values("instrument").unique())

    date_strs = [d.strftime("%Y-%m-%d") if hasattr(d, 'strftime') else str(d)[:10] for d in dates]
    print(f"  Dates: {date_strs[0]} ~ {date_strs[-1]} ({len(dates)} {'days' if not is_hourly else 'fake-days'})")
    print(f"  Instruments: {len(instruments)}")

    # 4. Create directories
    calendars_dir = output_path / "calendars"
    features_dir = output_path / "features"
    instruments_dir = output_path / "instruments"

    calendars_dir.mkdir(parents=True, exist_ok=True)
    features_dir.mkdir(parents=True, exist_ok=True)
    instruments_dir.mkdir(parents=True, exist_ok=True)

    # 5. Write calendars/day.txt
    cal_path = calendars_dir / "day.txt"
    with open(cal_path, "w") as f:
        for ds in date_strs:
            f.write(ds + "\n")
    print(f"  [OK] calendars/day.txt ({len(date_strs)} {'days' if not is_hourly else 'fake-days'})")

    # 6. Write instruments/all.txt (TAB-separated, NO header)
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

    # 7. Build date index lookup
    date_to_idx = {d: i for i, d in enumerate(date_strs)}
    n_dates = len(dates)

    # 8. Write feature .bin files for each instrument
    # Qlib format: [int32 start_index] + [float32 values for each date from start_index]
    h5_columns = [c for c in df.columns]

    for inst in instruments:
        inst_str = str(inst).lower()
        inst_dir = features_dir / inst_str
        inst_dir.mkdir(parents=True, exist_ok=True)
        inst_data = df.xs(str(inst), level="instrument")

        for h5_col in h5_columns:
            qlib_name = FIELD_MAP.get(h5_col, h5_col.lower().lstrip("$"))
            bin_path = inst_dir / f"{qlib_name}.{FREQ}.bin"

            # Build float32 array in calendar order
            arr = np.full(n_dates, np.nan, dtype=np.float32)
            inst_date_strs = [d.strftime("%Y-%m-%d") if hasattr(d, 'strftime') else str(d)[:10] for d in inst_data.index]
            for i, ds in enumerate(inst_date_strs):
                if ds in date_to_idx:
                    arr[date_to_idx[ds]] = float(inst_data.iloc[i][h5_col])

            with open(bin_path, "wb") as f:
                np.hstack([0, arr]).astype(np.float32).tofile(f)

        if inst == instruments[0]:
            first_file = inst_dir / f"close.{FREQ}.bin"
            data_read = np.fromfile(first_file, dtype=np.float32)
            print(f"  Verified {inst_str}/close.day.bin: {len(data_read)} float32 values "
                  f"(header={data_read[0]}, first_close={data_read[1]:.2f})")

    print(f"\n[SUCCESS] Qlib data created at: {output_path}")
    print(f"  calendars/day.txt: {len(date_strs)} {'days' if not is_hourly else 'fake-days'}")
    print(f"  instruments/all.txt: {len(instruments)} instruments")
    print(f"  features/: {len(instruments)} instruments x {len(h5_columns)} features")


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
