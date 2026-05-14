# CryptoAlpha — RD-Agent for Cryptocurrency Markets

CryptoAlpha is a cryptocurrency-adapted fork of [Microsoft RD-Agent](https://github.com/microsoft/RD-Agent), an autonomous framework that automates the research and development cycle for quantitative strategies.

We replaced the China A-share market stack with a complete cryptocurrency pipeline — from data ingestion to factor mining to backtesting — without modifying RD-Agent's core R&D loop logic.

## Key Differences

| Feature | RD-Agent (original) | CryptoAlpha |
|---------|-------------------|-------------|
| Market | China A-shares (CSI300) | Cryptocurrency futures |
| Trading hours | 9:30-15:00, weekdays only | 7×24 continuous |
| Adjustment factor | `$factor` col for ex-rights | `$factor=1.0` |
| Annualization | 252 trading days | 365 calendar days |
| Price limits | 10% daily limit | None |
| Instruments | Stock codes | Trading pairs (BTCUSDT, etc.) |
| Base features | Alpha158 (158 factors) | CryptoAlpha (90+ crypto factors) |
| Data source | Qlib China | Binance public API |

## Data Pipeline

```
Binance (1d, top-100 pairs, 99 downloaded)
  → generate_crypto.py → H5
  → convert_to_qlib_format.py → Qlib bin files
  → rdagent fin_factor / fin_quant
```

## Factor Sets

**CryptoAlpha** (`rdagent/utils/crypto_alpha.py`): K-line patterns, log-return momentum, log-scale volume, log-log correlations. Windows: 3–21 periods.

**Alpha158** (`rdagent/utils/qlib.py`): original A-share factors, kept for comparison.

Toggle with `CRYPTO_MODE=true/false`.

## Quick Start

```bash
conda create -n rdagent python=3.10 -y
conda activate rdagent
pip install pyqlib
pip install -r requirements.txt
pip install -e . --no-deps

# Configure .env (CRYPTO_MODE=true + API keys)
python init_crypto_data.py   # Download → convert → configure
rdagent fin_factor
```

## Architecture

Preserves RD-Agent's core R&D loop. All crypto adaptations controlled by `CRYPTO_MODE=true/false` — flip the switch and it falls back to A-share behavior.

```
Hypothesis → Code → Execution → Qlib Backtest → Feedback → Record
     ↑                                                        │
     └────────────────── Next Loop ───────────────────────────┘
```

Full modification details: `RD-Agent加密货币支持改造总结.md` (Chinese)
