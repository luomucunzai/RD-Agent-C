#!/usr/bin/env python
"""
一键初始化加密货币数据：下载 → 转换 H5 → 转换 Qlib 格式 → 配置时间范围

用法：
    python init_crypto_data.py                    # 全自动
    python init_crypto_data.py --skip-download    # 跳过下载（已有CSV）
    python init_crypto_data.py --debug            # 少量数据快速测试
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).parent


def run_step(step_name: str, cmd: list[str]):
    """Run a step with logging."""
    print(f"\n{'='*60}")
    print(f"  [{step_name}]")
    print(f"{'='*60}")
    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        print(f"  ❌ [{step_name}] FAILED (exit code {result.returncode})")
        sys.exit(1)
    print(f"  ✅ [{step_name}] OK")


def detect_date_range() -> tuple[str, str]:
    """Detect data date range from H5 file for conf.py."""
    h5_path = PROJECT_ROOT / "rdagent/scenarios/qlib/experiment/factor_data_template/daily_pv_all.h5"
    if not h5_path.exists():
        return "2024-05-14", "2026-04-20"

    df = pd.read_hdf(str(h5_path), key="data")
    dates = df.index.get_level_values("datetime").unique()
    start = dates.min()
    end = dates.max()

    # Leave 10 days margin for label computation
    train_end = start + (end - start) * 0.4
    valid_start = train_end + timedelta(days=1)
    valid_end = start + (end - start) * 0.7
    test_start = valid_end + timedelta(days=1)
    test_end = end - timedelta(days=10)

    return (
        start.strftime("%Y-%m-%d"),
        train_end.strftime("%Y-%m-%d"),
        valid_start.strftime("%Y-%m-%d"),
        valid_end.strftime("%Y-%m-%d"),
        test_start.strftime("%Y-%m-%d"),
        test_end.strftime("%Y-%m-%d"),
    )


def update_conf(start, train_end, valid_start, valid_end, test_start, test_end):
    """Update conf.py with detected date ranges."""
    conf_path = PROJECT_ROOT / "rdagent/app/qlib_rd_loop/conf.py"
    with open(conf_path) as f:
        content = f.read()

    # Update CRYPTO_MODE defaults
    import re
    content = re.sub(
        r'_DEFAULT_TRAIN_START = "[\d-]+"',
        f'_DEFAULT_TRAIN_START = "{start}"',
        content,
    )
    content = re.sub(
        r'_DEFAULT_TRAIN_END = "[\d-]+"',
        f'_DEFAULT_TRAIN_END = "{train_end}"',
        content,
    )
    content = re.sub(
        r'_DEFAULT_VALID_START = "[\d-]+"',
        f'_DEFAULT_VALID_START = "{valid_start}"',
        content,
    )
    content = re.sub(
        r'_DEFAULT_VALID_END = "[\d-]+"',
        f'_DEFAULT_VALID_END = "{valid_end}"',
        content,
    )
    content = re.sub(
        r'_DEFAULT_TEST_START = "[\d-]+"',
        f'_DEFAULT_TEST_START = "{test_start}"',
        content,
    )
    content = re.sub(
        r'_DEFAULT_TEST_END = "[\d-]+"',
        f'_DEFAULT_TEST_END = "{test_end}"',
        content,
    )

    with open(conf_path, "w") as f:
        f.write(content)

    print(f"  📅 时间范围: train={start}~{train_end}, valid={valid_start}~{valid_end}, test={test_start}~{test_end}")


def main():
    parser = argparse.ArgumentParser(description="Initialize crypto data pipeline")
    parser.add_argument("--skip-download", action="store_true", help="Skip Binance download")
    parser.add_argument("--debug", action="store_true", help="Use debug mode (subset)")
    args = parser.parse_args()

    print(r"""
   ╔══════════════════════════════════════════╗
   ║  加密货币数据初始化流水线                  ║
   ║  Binance CSV → H5 → Qlib bin → 回测就绪   ║
   ╚══════════════════════════════════════════╝
    """)

    # Step 1: Download Binance data
    if not args.skip_download:
        csv_dir = PROJECT_ROOT / "binance_futures_data"
        if csv_dir.exists() and list(csv_dir.glob("*.csv")):
            print("  📦 CSV 数据已存在，跳过下载（加 --skip-download 强制跳过）")
        else:
            run_step("下载币安数据", ["python", "downdata.py"])
    else:
        print("  ⏭️  跳过下载")

    # Step 2: Convert CSV to H5
    run_step("CSV → H5", [
        "python",
        "rdagent/scenarios/qlib/experiment/factor_data_template/generate_crypto.py",
        *(["--debug"] if args.debug else []),
    ])

    # Step 3: Convert H5 to Qlib native format
    h5_path = PROJECT_ROOT / "rdagent/scenarios/qlib/experiment/factor_data_template/daily_pv_all.h5"
    if not h5_path.exists():
        h5_path = PROJECT_ROOT / "rdagent/scenarios/qlib/experiment/factor_data_template/daily_pv_debug.h5"

    run_step("H5 → Qlib 原生格式", [
        "python",
        "rdagent/scenarios/qlib/experiment/factor_data_template/convert_to_qlib_format.py",
        "--h5", str(h5_path),
    ])

    # Step 4: Detect date range and update conf.py
    start, train_end, valid_start, valid_end, test_start, test_end = detect_date_range()
    update_conf(start, train_end, valid_start, valid_end, test_start, test_end)

    # Done!
    print(f"""
   ╔══════════════════════════════════════════╗
   ║  ✅ 初始化完成！                           ║
   ║  数据路径: ~/.qlib/qlib_data/cn_data/      ║
   ║  时间范围: {start} ~ {test_end}            ║
   ║                                          ║
   ║  运行: conda activate rdagent             ║
   ║        rdagent fin_factor                 ║
   ╚══════════════════════════════════════════╝
    """)


if __name__ == "__main__":
    main()
