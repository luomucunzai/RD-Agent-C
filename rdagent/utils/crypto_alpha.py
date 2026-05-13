"""
CryptoAlpha — Cryptocurrency-adapted factor set.

Designed for 7x24 continuous trading cryptocurrency markets.
Differences from A-share Alpha158:
- No $vwap (use CPOS = price position instead)
- Max window 21 days (crypto changes faster, 60d is too slow)
- Log returns for better normality in crypto's volatile regime
- Volume factors use Log scale (crypto volume spans orders of magnitude)
- Log-log correlation for price-volume relationships
- Shorter labels for crypto's 24h trading cycle

Usage:
    from rdagent.utils.crypto_alpha import CRYPTO_20, CRYPTO_ALPHA
"""

CRYPTO_ALPHA = {
    # ── K-line Pattern (adapted, no $vwap) ──
    "CKMID": "($close-$open)/$open",
    "CKLEN": "($high-$low)/$open",
    "CKMID2": "($close-$open)/($high-$low+1e-12)",
    "CKUP": "($high-Greater($open, $close))/$open",
    "CKUP2": "($high-Greater($open, $close))/($high-$low+1e-12)",
    "CKLOW": "(Less($open, $close)-$low)/$open",
    "CKLOW2": "(Less($open, $close)-$low)/($high-$low+1e-12)",
    "CKSFT": "(2*$close-$high-$low)/$open",
    "CKSFT2": "(2*$close-$high-$low)/($high-$low+1e-12)",
    "COPEN0": "$open/$close",
    "CHIGH0": "$high/$close",
    "CLOW0": "$low/$close",
    "CPOS": "(2*$close-$high-$low)/($high-$low+1e-12)",       # Replaces VWAP0

    # ── Short-term Momentum (3-21 days) ──
    "CROC3": "Ref($close, 3)/$close",
    "CROC5": "Ref($close, 5)/$close",
    "CROC10": "Ref($close, 10)/$close",
    "CROC15": "Ref($close, 15)/$close",
    "CROC21": "Ref($close, 21)/$close",

    # ── Log Return Momentum ──
    "CLRET3": "Log($close/Ref($close, 3))",
    "CLRET5": "Log($close/Ref($close, 5))",
    "CLRET10": "Log($close/Ref($close, 10))",
    "CLRET21": "Log($close/Ref($close, 21))",

    # ── Moving Average ──
    "CMA3": "Mean($close, 3)/$close",
    "CMA5": "Mean($close, 5)/$close",
    "CMA10": "Mean($close, 10)/$close",
    "CMA15": "Mean($close, 15)/$close",
    "CMA21": "Mean($close, 21)/$close",

    # ── Volatility (price + log-return) ──
    "CSTD3": "Std($close, 3)/$close",
    "CSTD5": "Std($close, 5)/$close",
    "CSTD10": "Std($close, 10)/$close",
    "CSTD15": "Std($close, 15)/$close",
    "CSTD21": "Std($close, 21)/$close",
    "CLSTD5": "Std(Log($close/Ref($close,1)), 5)",
    "CLSTD10": "Std(Log($close/Ref($close,1)), 10)",
    "CLSTD21": "Std(Log($close/Ref($close,1)), 21)",

    # ── Trend Strength (R-squared) ──
    "CRSQR5": "Rsquare($close, 5)",
    "CRSQR10": "Rsquare($close, 10)",
    "CRSQR15": "Rsquare($close, 15)",
    "CRSQR21": "Rsquare($close, 21)",

    # ── Price Extremes ──
    "CMAX5": "Max($high, 5)/$close",
    "CMAX10": "Max($high, 10)/$close",
    "CMAX15": "Max($high, 15)/$close",
    "CMAX21": "Max($high, 21)/$close",
    "CMIN5": "Min($low, 5)/$close",
    "CMIN10": "Min($low, 10)/$close",
    "CMIN15": "Min($low, 15)/$close",
    "CMIN21": "Min($low, 21)/$close",

    # ── RSV / Stochastic ──
    "CRSV5": "($close-Min($low, 5))/(Max($high, 5)-Min($low, 5)+1e-12)",
    "CRSV10": "($close-Min($low, 10))/(Max($high, 10)-Min($low, 10)+1e-12)",
    "CRSV21": "($close-Min($low, 21))/(Max($high, 21)-Min($low, 21)+1e-12)",

    # ── Volume Correlation (Log-Log scale) ──
    "CCORR5": "Corr(Log($close), Log($volume+1), 5)",
    "CCORR10": "Corr(Log($close), Log($volume+1), 10)",
    "CCORR21": "Corr(Log($close), Log($volume+1), 21)",
    "CCORD5": "Corr(Log($close/Ref($close,1)), Log($volume/Ref($volume,1)+1), 5)",
    "CCORD10": "Corr(Log($close/Ref($close,1)), Log($volume/Ref($volume,1)+1), 10)",
    "CCORD21": "Corr(Log($close/Ref($close,1)), Log($volume/Ref($volume,1)+1), 21)",

    # ── Volume (Log scale) ──
    "CVMA5": "Log(Mean($volume, 5))/(Log($volume)+1e-12)",
    "CVMA10": "Log(Mean($volume, 10))/(Log($volume)+1e-12)",
    "CVMA21": "Log(Mean($volume, 21))/(Log($volume)+1e-12)",
    "CVSTD5": "Std(Log($volume), 5)",
    "CVSTD10": "Std(Log($volume), 10)",
    "CVSTD21": "Std(Log($volume), 21)",
    "CVOLCH5": "Log($volume/Ref($volume,5))",
    "CVOLCH10": "Log($volume/Ref($volume,10))",
    "CVOLCH21": "Log($volume/Ref($volume,21))",

    # ── Up/Down Days ──
    "CCNTP5": "Mean($close>Ref($close, 1), 5)",
    "CCNTP10": "Mean($close>Ref($close, 1), 10)",
    "CCNTP21": "Mean($close>Ref($close, 1), 21)",
    "CCNTD5": "Mean($close>Ref($close, 1), 5)-Mean($close<Ref($close, 1), 5)",
    "CCNTD10": "Mean($close>Ref($close, 1), 10)-Mean($close<Ref($close, 1), 10)",
    "CCNTD21": "Mean($close>Ref($close, 1), 21)-Mean($close<Ref($close, 1), 21)",

    # ── Price-Volume Interaction ──
    "CPVVOL5": "Corr($close, $volume, 5)",
    "CPVVOL10": "Corr($close, $volume, 10)",
    "CPVVOL21": "Corr($close, $volume, 21)",
}

# Default 25 base factors used as CRYPTO_20
CRYPTO_20 = {
    "CKLEN": "($high-$low)/$open",
    "CPOS": "(2*$close-$high-$low)/($high-$low+1e-12)",
    "COPEN0": "$open/$close",
    "CKUP": "($high-Greater($open, $close))/$open",
    "CROC5": "Ref($close, 5)/$close",
    "CROC10": "Ref($close, 10)/$close",
    "CROC21": "Ref($close, 21)/$close",
    "CLRET10": "Log($close/Ref($close, 10))",
    "CSTD10": "Std($close, 10)/$close",
    "CLSTD10": "Std(Log($close/Ref($close,1)), 10)",
    "CRSQR10": "Rsquare($close, 10)",
    "CRSV10": "($close-Min($low, 10))/(Max($high, 10)-Min($low, 10)+1e-12)",
    "CCORR10": "Corr(Log($close), Log($volume+1), 10)",
    "CCORD10": "Corr(Log($close/Ref($close,1)), Log($volume/Ref($volume,1)+1), 10)",
    "CVMA10": "Log(Mean($volume, 10))/(Log($volume)+1e-12)",
    "CVSTD10": "Std(Log($volume), 10)",
    "CVOLCH10": "Log($volume/Ref($volume,10))",
    "CMAX10": "Max($high, 10)/$close",
    "CMIN10": "Min($low, 10)/$close",
    "CCNTP5": "Mean($close>Ref($close, 1), 5)",
    "CCNTD10": "Mean($close>Ref($close, 1), 10)-Mean($close<Ref($close, 1), 10)",
    "CPVVOL10": "Corr($close, $volume, 10)",
    "CSTD5": "Std($close, 5)/$close",
    "CKSFT": "(2*$close-$high-$low)/$open",
    "CVSTD5": "Std(Log($volume), 5)",
}
