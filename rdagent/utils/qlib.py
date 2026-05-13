"""
Qlib factor definitions for stock (Alpha158) and cryptocurrency markets.

CRYPTO_MODE=true uses CRYPTO_ALPHA factors adapted for 7x24 continuous trading:
- Shorter windows (max 30 days, crypto changes faster than stocks)
- No $vwap (not available in crypto OHLCV data)
- Log returns instead of simple returns for better normality
- Volume factors adapted for crypto's extreme volume ranges
"""

ALPHA20 = {
    "RESI5": "Resi($close, 5)/$close",
    "WVMA5": "Std(Abs($close/Ref($close, 1)-1)*$volume, 5)/(Mean(Abs($close/Ref($close, 1)-1)*$volume, 5)+1e-12)",
    "RSQR5": "Rsquare($close, 5)",
    "KLEN": "($high-$low)/$open",
    "RSQR10": "Rsquare($close, 10)",
    "CORR5": "Corr($close, Log($volume+1), 5)",
    "CORD5": "Corr($close/Ref($close,1), Log($volume/Ref($volume, 1)+1), 5)",
    "CORR10": "Corr($close, Log($volume+1), 10)",
    "ROC60": "Ref($close, 60)/$close",
    "RESI10": "Resi($close, 10)/$close",
    "VSTD5": "Std($volume, 5)/($volume+1e-12)",
    "RSQR60": "Rsquare($close, 60)",
    "CORR60": "Corr($close, Log($volume+1), 60)",
    "WVMA60": "Std(Abs($close/Ref($close, 1)-1)*$volume, 60)/(Mean(Abs($close/Ref($close, 1)-1)*$volume, 60)+1e-12)",
    "STD5": "Std($close, 5)/$close",
    "RSQR20": "Rsquare($close, 20)",
    "CORD60": "Corr($close/Ref($close,1), Log($volume/Ref($volume, 1)+1), 60)",
    "CORD10": "Corr($close/Ref($close,1), Log($volume/Ref($volume, 1)+1), 10)",
    "CORR20": "Corr($close, Log($volume+1), 20)",
    "KLOW": "(Less($open, $close)-$low)/$open",
}

ALPHA158 = {
    "KMID": "($close-$open)/$open",
    "KLEN": "($high-$low)/$open",
    "KMID2": "($close-$open)/($high-$low+1e-12)",
    "KUP": "($high-Greater($open, $close))/$open",
    "KUP2": "($high-Greater($open, $close))/($high-$low+1e-12)",
    "KLOW": "(Less($open, $close)-$low)/$open",
    "KLOW2": "(Less($open, $close)-$low)/($high-$low+1e-12)",
    "KSFT": "(2*$close-$high-$low)/$open",
    "KSFT2": "(2*$close-$high-$low)/($high-$low+1e-12)",
    "OPEN0": "$open/$close",
    "HIGH0": "$high/$close",
    "LOW0": "$low/$close",
    "VWAP0": "$vwap/$close",
    "ROC5": "Ref($close, 5)/$close",
    "ROC10": "Ref($close, 10)/$close",
    "ROC20": "Ref($close, 20)/$close",
    "ROC30": "Ref($close, 30)/$close",
    "ROC60": "Ref($close, 60)/$close",
    "MA5": "Mean($close, 5)/$close",
    "MA10": "Mean($close, 10)/$close",
    "MA20": "Mean($close, 20)/$close",
    "MA30": "Mean($close, 30)/$close",
    "MA60": "Mean($close, 60)/$close",
    "STD5": "Std($close, 5)/$close",
    "STD10": "Std($close, 10)/$close",
    "STD20": "Std($close, 20)/$close",
    "STD30": "Std($close, 30)/$close",
    "STD60": "Std($close, 60)/$close",
    "BETA5": "Slope($close, 5)/$close",
    "BETA10": "Slope($close, 10)/$close",
    "BETA20": "Slope($close, 20)/$close",
    "BETA30": "Slope($close, 30)/$close",
    "BETA60": "Slope($close, 60)/$close",
    "RSQR5": "Rsquare($close, 5)",
    "RSQR10": "Rsquare($close, 10)",
    "RSQR20": "Rsquare($close, 20)",
    "RSQR30": "Rsquare($close, 30)",
    "RSQR60": "Rsquare($close, 60)",
    "RESI5": "Resi($close, 5)/$close",
    "RESI10": "Resi($close, 10)/$close",
    "RESI20": "Resi($close, 20)/$close",
    "RESI30": "Resi($close, 30)/$close",
    "RESI60": "Resi($close, 60)/$close",
    "MAX5": "Max($high, 5)/$close",
    "MAX10": "Max($high, 10)/$close",
    "MAX20": "Max($high, 20)/$close",
    "MAX30": "Max($high, 30)/$close",
    "MAX60": "Max($high, 60)/$close",
    "MIN5": "Min($low, 5)/$close",
    "MIN10": "Min($low, 10)/$close",
    "MIN20": "Min($low, 20)/$close",
    "MIN30": "Min($low, 30)/$close",
    "MIN60": "Min($low, 60)/$close",
    "QTLU5": "Quantile($close, 5, 0.8)/$close",
    "QTLU10": "Quantile($close, 10, 0.8)/$close",
    "QTLU20": "Quantile($close, 20, 0.8)/$close",
    "QTLU30": "Quantile($close, 30, 0.8)/$close",
    "QTLU60": "Quantile($close, 60, 0.8)/$close",
    "QTLD5": "Quantile($close, 5, 0.2)/$close",
    "QTLD10": "Quantile($close, 10, 0.2)/$close",
    "QTLD20": "Quantile($close, 20, 0.2)/$close",
    "QTLD30": "Quantile($close, 30, 0.2)/$close",
    "QTLD60": "Quantile($close, 60, 0.2)/$close",
    "RANK5": "Rank($close, 5)",
    "RANK10": "Rank($close, 10)",
    "RANK20": "Rank($close, 20)",
    "RANK30": "Rank($close, 30)",
    "RANK60": "Rank($close, 60)",
    "RSV5": "($close-Min($low, 5))/(Max($high, 5)-Min($low, 5)+1e-12)",
    "RSV10": "($close-Min($low, 10))/(Max($high, 10)-Min($low, 10)+1e-12)",
    "RSV20": "($close-Min($low, 20))/(Max($high, 20)-Min($low, 20)+1e-12)",
    "RSV30": "($close-Min($low, 30))/(Max($high, 30)-Min($low, 30)+1e-12)",
    "RSV60": "($close-Min($low, 60))/(Max($high, 60)-Min($low, 60)+1e-12)",
    "IMAX5": "IdxMax($high, 5)/5",
    "IMAX10": "IdxMax($high, 10)/10",
    "IMAX20": "IdxMax($high, 20)/20",
    "IMAX30": "IdxMax($high, 30)/30",
    "IMAX60": "IdxMax($high, 60)/60",
    "IMIN5": "IdxMin($low, 5)/5",
    "IMIN10": "IdxMin($low, 10)/10",
    "IMIN20": "IdxMin($low, 20)/20",
    "IMIN30": "IdxMin($low, 30)/30",
    "IMIN60": "IdxMin($low, 60)/60",
    "IMXD5": "(IdxMax($high, 5)-IdxMin($low, 5))/5",
    "IMXD10": "(IdxMax($high, 10)-IdxMin($low, 10))/10",
    "IMXD20": "(IdxMax($high, 20)-IdxMin($low, 20))/20",
    "IMXD30": "(IdxMax($high, 30)-IdxMin($low, 30))/30",
    "IMXD60": "(IdxMax($high, 60)-IdxMin($low, 60))/60",
    "CORR5": "Corr($close, Log($volume+1), 5)",
    "CORR10": "Corr($close, Log($volume+1), 10)",
    "CORR20": "Corr($close, Log($volume+1), 20)",
    "CORR30": "Corr($close, Log($volume+1), 30)",
    "CORR60": "Corr($close, Log($volume+1), 60)",
    "CORD5": "Corr($close/Ref($close,1), Log($volume/Ref($volume, 1)+1), 5)",
    "CORD10": "Corr($close/Ref($close,1), Log($volume/Ref($volume, 1)+1), 10)",
    "CORD20": "Corr($close/Ref($close,1), Log($volume/Ref($volume, 1)+1), 20)",
    "CORD30": "Corr($close/Ref($close,1), Log($volume/Ref($volume, 1)+1), 30)",
    "CORD60": "Corr($close/Ref($close,1), Log($volume/Ref($volume, 1)+1), 60)",
    "CNTP5": "Mean($close>Ref($close, 1), 5)",
    "CNTP10": "Mean($close>Ref($close, 1), 10)",
    "CNTP20": "Mean($close>Ref($close, 1), 20)",
    "CNTP30": "Mean($close>Ref($close, 1), 30)",
    "CNTP60": "Mean($close>Ref($close, 1), 60)",
    "CNTN5": "Mean($close<Ref($close, 1), 5)",
    "CNTN10": "Mean($close<Ref($close, 1), 10)",
    "CNTN20": "Mean($close<Ref($close, 1), 20)",
    "CNTN30": "Mean($close<Ref($close, 1), 30)",
    "CNTN60": "Mean($close<Ref($close, 1), 60)",
    "CNTD5": "Mean($close>Ref($close, 1), 5)-Mean($close<Ref($close, 1), 5)",
    "CNTD10": "Mean($close>Ref($close, 1), 10)-Mean($close<Ref($close, 1), 10)",
    "CNTD20": "Mean($close>Ref($close, 1), 20)-Mean($close<Ref($close, 1), 20)",
    "CNTD30": "Mean($close>Ref($close, 1), 30)-Mean($close<Ref($close, 1), 30)",
    "CNTD60": "Mean($close>Ref($close, 1), 60)-Mean($close<Ref($close, 1), 60)",
    "SUMP5": "Sum(Greater($close-Ref($close, 1), 0), 5)/(Sum(Abs($close-Ref($close, 1)), 5)+1e-12)",
    "SUMP10": "Sum(Greater($close-Ref($close, 1), 0), 10)/(Sum(Abs($close-Ref($close, 1)), 10)+1e-12)",
    "SUMP20": "Sum(Greater($close-Ref($close, 1), 0), 20)/(Sum(Abs($close-Ref($close, 1)), 20)+1e-12)",
    "SUMP30": "Sum(Greater($close-Ref($close, 1), 0), 30)/(Sum(Abs($close-Ref($close, 1)), 30)+1e-12)",
    "SUMP60": "Sum(Greater($close-Ref($close, 1), 0), 60)/(Sum(Abs($close-Ref($close, 1)), 60)+1e-12)",
    "SUMN5": "Sum(Greater(Ref($close, 1)-$close, 0), 5)/(Sum(Abs($close-Ref($close, 1)), 5)+1e-12)",
    "SUMN10": "Sum(Greater(Ref($close, 1)-$close, 0), 10)/(Sum(Abs($close-Ref($close, 1)), 10)+1e-12)",
    "SUMN20": "Sum(Greater(Ref($close, 1)-$close, 0), 20)/(Sum(Abs($close-Ref($close, 1)), 20)+1e-12)",
    "SUMN30": "Sum(Greater(Ref($close, 1)-$close, 0), 30)/(Sum(Abs($close-Ref($close, 1)), 30)+1e-12)",
    "SUMN60": "Sum(Greater(Ref($close, 1)-$close, 0), 60)/(Sum(Abs($close-Ref($close, 1)), 60)+1e-12)",
    "SUMD5": "(Sum(Greater($close-Ref($close, 1), 0), 5)-Sum(Greater(Ref($close, 1)-$close, 0), 5))/(Sum(Abs($close-Ref($close, 1)), 5)+1e-12)",
    "SUMD10": "(Sum(Greater($close-Ref($close, 1), 0), 10)-Sum(Greater(Ref($close, 1)-$close, 0), 10))/(Sum(Abs($close-Ref($close, 1)), 10)+1e-12)",
    "SUMD20": "(Sum(Greater($close-Ref($close, 1), 0), 20)-Sum(Greater(Ref($close, 1)-$close, 0), 20))/(Sum(Abs($close-Ref($close, 1)), 20)+1e-12)",
    "SUMD30": "(Sum(Greater($close-Ref($close, 1), 0), 30)-Sum(Greater(Ref($close, 1)-$close, 0), 30))/(Sum(Abs($close-Ref($close, 1)), 30)+1e-12)",
    "SUMD60": "(Sum(Greater($close-Ref($close, 1), 0), 60)-Sum(Greater(Ref($close, 1)-$close, 0), 60))/(Sum(Abs($close-Ref($close, 1)), 60)+1e-12)",
    "VMA5": "Mean($volume, 5)/($volume+1e-12)",
    "VMA10": "Mean($volume, 10)/($volume+1e-12)",
    "VMA20": "Mean($volume, 20)/($volume+1e-12)",
    "VMA30": "Mean($volume, 30)/($volume+1e-12)",
    "VMA60": "Mean($volume, 60)/($volume+1e-12)",
    "VSTD5": "Std($volume, 5)/($volume+1e-12)",
    "VSTD10": "Std($volume, 10)/($volume+1e-12)",
    "VSTD20": "Std($volume, 20)/($volume+1e-12)",
    "VSTD30": "Std($volume, 30)/($volume+1e-12)",
    "VSTD60": "Std($volume, 60)/($volume+1e-12)",
    "WVMA5": "Std(Abs($close/Ref($close, 1)-1)*$volume, 5)/(Mean(Abs($close/Ref($close, 1)-1)*$volume, 5)+1e-12)",
    "WVMA10": "Std(Abs($close/Ref($close, 1)-1)*$volume, 10)/(Mean(Abs($close/Ref($close, 1)-1)*$volume, 10)+1e-12)",
    "WVMA20": "Std(Abs($close/Ref($close, 1)-1)*$volume, 20)/(Mean(Abs($close/Ref($close, 1)-1)*$volume, 20)+1e-12)",
    "WVMA30": "Std(Abs($close/Ref($close, 1)-1)*$volume, 30)/(Mean(Abs($close/Ref($close, 1)-1)*$volume, 30)+1e-12)",
    "WVMA60": "Std(Abs($close/Ref($close, 1)-1)*$volume, 60)/(Mean(Abs($close/Ref($close, 1)-1)*$volume, 60)+1e-12)",
    "VSUMP5": "Sum(Greater($volume-Ref($volume, 1), 0), 5)/(Sum(Abs($volume-Ref($volume, 1)), 5)+1e-12)",
    "VSUMP10": "Sum(Greater($volume-Ref($volume, 1), 0), 10)/(Sum(Abs($volume-Ref($volume, 1)), 10)+1e-12)",
    "VSUMP20": "Sum(Greater($volume-Ref($volume, 1), 0), 20)/(Sum(Abs($volume-Ref($volume, 1)), 20)+1e-12)",
    "VSUMP30": "Sum(Greater($volume-Ref($volume, 1), 0), 30)/(Sum(Abs($volume-Ref($volume, 1)), 30)+1e-12)",
    "VSUMP60": "Sum(Greater($volume-Ref($volume, 1), 0), 60)/(Sum(Abs($volume-Ref($volume, 1)), 60)+1e-12)",
    "VSUMN5": "Sum(Greater(Ref($volume, 1)-$volume, 0), 5)/(Sum(Abs($volume-Ref($volume, 1)), 5)+1e-12)",
    "VSUMN10": "Sum(Greater(Ref($volume, 1)-$volume, 0), 10)/(Sum(Abs($volume-Ref($volume, 1)), 10)+1e-12)",
    "VSUMN20": "Sum(Greater(Ref($volume, 1)-$volume, 0), 20)/(Sum(Abs($volume-Ref($volume, 1)), 20)+1e-12)",
    "VSUMN30": "Sum(Greater(Ref($volume, 1)-$volume, 0), 30)/(Sum(Abs($volume-Ref($volume, 1)), 30)+1e-12)",
    "VSUMN60": "Sum(Greater(Ref($volume, 1)-$volume, 0), 60)/(Sum(Abs($volume-Ref($volume, 1)), 60)+1e-12)",
    "VSUMD5": "(Sum(Greater($volume-Ref($volume, 1), 0), 5)-Sum(Greater(Ref($volume, 1)-$volume, 0), 5))/(Sum(Abs($volume-Ref($volume, 1)), 5)+1e-12)",
    "VSUMD10": "(Sum(Greater($volume-Ref($volume, 1), 0), 10)-Sum(Greater(Ref($volume, 1)-$volume, 0), 10))/(Sum(Abs($volume-Ref($volume, 1)), 10)+1e-12)",
    "VSUMD20": "(Sum(Greater($volume-Ref($volume, 1), 0), 20)-Sum(Greater(Ref($volume, 1)-$volume, 0), 20))/(Sum(Abs($volume-Ref($volume, 1)), 20)+1e-12)",
    "VSUMD30": "(Sum(Greater($volume-Ref($volume, 1), 0), 30)-Sum(Greater(Ref($volume, 1)-$volume, 0), 30))/(Sum(Abs($volume-Ref($volume, 1)), 30)+1e-12)",
    "VSUMD60": "(Sum(Greater($volume-Ref($volume, 1), 0), 60)-Sum(Greater(Ref($volume, 1)-$volume, 0), 60))/(Sum(Abs($volume-Ref($volume, 1)), 60)+1e-12)",
}


# ============================================================
# Crypto-adapted factors (used when CRYPTO_MODE=true)
# Adaptations vs Alpha158:
# - No $vwap (not in crypto data), replaced with OHLC-based price position
# - Shorter max window: 30 days (crypto changes faster, 60d is too slow)
# - Added 3-day short-term windows for crypto's faster signals
# - Returns use Log for better normality in crypto's volatile regime
# - Volume factors use Log scale (crypto volume spans many orders of magnitude)
# - Label: single-period forward return (faster signal for crypto's 24h cycle)
# ============================================================

CRYPTO_ALPHA = {
    # --- K-line Pattern (adapted, no $vwap) ---
    "CKMID": "($close-$open)/$open",                           # Same as KMID
    "CKLEN": "($high-$low)/$open",                              # Same as KLEN
    "CKMID2": "($close-$open)/($high-$low+1e-12)",             # Same as KMID2
    "CKUP": "($high-Greater($open, $close))/$open",             # Same as KUP
    "CKLOW": "(Less($open, $close)-$low)/$open",                # Same as KLOW
    "CKSFT": "(2*$close-$high-$low)/$open",                     # Same as KSFT
    "COPEN0": "$open/$close",                                    # Same as OPEN0
    "CHIGH0": "$high/$close",                                    # Same as HIGH0
    "CLOW0": "$low/$close",                                      # Same as LOW0
    "CPOS": "(2*$close-$high-$low)/($high-$low+1e-12)",         # Price position (replaces VWAP0)

    # --- Short-term Momentum (3-15 days, crypto moves fast) ---
    "CROC3": "Ref($close, 3)/$close",                           # 3-day momentum (new, crypto short-term)
    "CROC5": "Ref($close, 5)/$close",                           # 5-day momentum
    "CROC10": "Ref($close, 10)/$close",                         # 10-day momentum
    "CROC15": "Ref($close, 15)/$close",                         # 15-day momentum (new)
    "CROC21": "Ref($close, 21)/$close",                         # 21-day = ~3 weeks

    # --- Log Return Momentum (better for crypto's log-normal distribution) ---
    "CLRET3": "Log($close/Ref($close, 3))",                     # 3d log return (new)
    "CLRET5": "Log($close/Ref($close, 5))",                     # 5d log return (new)
    "CLRET10": "Log($close/Ref($close, 10))",                   # 10d log return (new)
    "CLRET21": "Log($close/Ref($close, 21))",                   # 21d log return (new)

    # --- Moving Average (shorter windows for crypto) ---
    "CMA3": "Mean($close, 3)/$close",
    "CMA5": "Mean($close, 5)/$close",
    "CMA10": "Mean($close, 10)/$close",
    "CMA15": "Mean($close, 15)/$close",
    "CMA21": "Mean($close, 21)/$close",

    # --- Volatility (shorter + log returns) ---
    "CSTD3": "Std($close, 3)/$close",
    "CSTD5": "Std($close, 5)/$close",
    "CSTD10": "Std($close, 10)/$close",
    "CSTD15": "Std($close, 15)/$close",
    "CSTD21": "Std($close, 21)/$close",
    "CLSTD5": "Std(Log($close/Ref($close,1)), 5)",              # Log-return volatility (new)
    "CLSTD10": "Std(Log($close/Ref($close,1)), 10)",            # Log-return volatility (new)
    "CLSTD21": "Std(Log($close/Ref($close,1)), 21)",            # Log-return volatility (new)

    # --- Trend Strength (R-squared from linear regression) ---
    "CRSQR5": "Rsquare($close, 5)",
    "CRSQR10": "Rsquare($close, 10)",
    "CRSQR15": "Rsquare($close, 15)",
    "CRSQR21": "Rsquare($close, 21)",

    # --- Price Extremes (shorter windows) ---
    "CMAX5": "Max($high, 5)/$close",
    "CMAX10": "Max($high, 10)/$close",
    "CMAX15": "Max($high, 15)/$close",
    "CMAX21": "Max($high, 21)/$close",
    "CMIN5": "Min($low, 5)/$close",
    "CMIN10": "Min($low, 10)/$close",
    "CMIN15": "Min($low, 15)/$close",
    "CMIN21": "Min($low, 21)/$close",

    # --- RSV / Stochastic (shorter) ---
    "CRSV5": "($close-Min($low, 5))/(Max($high, 5)-Min($low, 5)+1e-12)",
    "CRSV10": "($close-Min($low, 10))/(Max($high, 10)-Min($low, 10)+1e-12)",
    "CRSV21": "($close-Min($low, 21))/(Max($high, 21)-Min($low, 21)+1e-12)",

    # --- Volume Correlation (Log scale for crypto's extreme ranges) ---
    "CCORR5": "Corr(Log($close), Log($volume+1), 5)",           # Log-log correlation (new, better for crypto)
    "CCORR10": "Corr(Log($close), Log($volume+1), 10)",
    "CCORR21": "Corr(Log($close), Log($volume+1), 21)",
    "CCORD5": "Corr(Log($close/Ref($close,1)), Log($volume/Ref($volume,1)+1), 5)",  # Log-return x volume-change
    "CCORD10": "Corr(Log($close/Ref($close,1)), Log($volume/Ref($volume,1)+1), 10)",
    "CCORD21": "Corr(Log($close/Ref($close,1)), Log($volume/Ref($volume,1)+1), 21)",

    # --- Volume (Log scale) ---
    "CVMA5": "Log(Mean($volume, 5))/(Log($volume)+1e-12)",      # Log volume ratio (new)
    "CVMA10": "Log(Mean($volume, 10))/(Log($volume)+1e-12)",
    "CVMA21": "Log(Mean($volume, 21))/(Log($volume)+1e-12)",
    "CVSTD5": "Std(Log($volume), 5)",                           # Log-vol volatility (new)
    "CVSTD10": "Std(Log($volume), 10)",
    "CVSTD21": "Std(Log($volume), 21)",

    # --- Volume Change Direction ---
    "CVOLCH5": "Log($volume/Ref($volume,5))",                   # 5d volume change (log ratio)
    "CVOLCH10": "Log($volume/Ref($volume,10))",                 # 10d volume change
    "CVOLCH21": "Log($volume/Ref($volume,21))",                 # 21d volume change

    # --- Up/Down Days Count ---
    "CCNTP5": "Mean($close>Ref($close, 1), 5)",                 # Same as CNTP
    "CCNTP10": "Mean($close>Ref($close, 1), 10)",
    "CCNTP21": "Mean($close>Ref($close, 1), 21)",
    "CCNTD5": "Mean($close>Ref($close, 1), 5)-Mean($close<Ref($close, 1), 5)",  # Net up ratio
    "CCNTD10": "Mean($close>Ref($close, 1), 10)-Mean($close<Ref($close, 1), 10)",
    "CCNTD21": "Mean($close>Ref($close, 1), 21)-Mean($close<Ref($close, 1), 21)",

    # --- Price-Volume Interaction ---
    "CPVVOL5": "Corr($close, $volume, 5)",                      # Raw price-volume corr (no Log, for comparison)
    "CPVVOL10": "Corr($close, $volume, 10)",
    "CPVVOL21": "Corr($close, $volume, 21)",
}

# Default 25 crypto factors used as base features
CRYPTO_20 = {
    # K-line patterns (4)
    "CKLEN": "($high-$low)/$open",
    "CPOS": "(2*$close-$high-$low)/($high-$low+1e-12)",
    "COPEN0": "$open/$close",
    "CKUP": "($high-Greater($open, $close))/$open",

    # Momentum (4)
    "CROC5": "Ref($close, 5)/$close",
    "CROC10": "Ref($close, 10)/$close",
    "CROC21": "Ref($close, 21)/$close",
    "CLRET10": "Log($close/Ref($close, 10))",

    # Volatility (4)
    "CSTD10": "Std($close, 10)/$close",
    "CLSTD10": "Std(Log($close/Ref($close,1)), 10)",
    "CRSQR10": "Rsquare($close, 10)",
    "CRSV10": "($close-Min($low, 10))/(Max($high, 10)-Min($low, 10)+1e-12)",

    # Volume (5)
    "CCORR10": "Corr(Log($close), Log($volume+1), 10)",
    "CCORD10": "Corr(Log($close/Ref($close,1)), Log($volume/Ref($volume,1)+1), 10)",
    "CVMA10": "Log(Mean($volume, 10))/(Log($volume)+1e-12)",
    "CVSTD10": "Std(Log($volume), 10)",
    "CVOLCH10": "Log($volume/Ref($volume,10))",

    # Trend/Risk (4)
    "CMAX10": "Max($high, 10)/$close",
    "CMIN10": "Min($low, 10)/$close",
    "CCNTP5": "Mean($close>Ref($close, 1), 5)",
    "CCNTD10": "Mean($close>Ref($close, 1), 10)-Mean($close<Ref($close, 1), 10)",

    # Price-Volume (4)
    "CPVVOL10": "Corr($close, $volume, 10)",
    "CSTD5": "Std($close, 5)/$close",
    "CKSFT": "(2*$close-$high-$low)/$open",
    "CVSTD5": "Std(Log($volume), 5)",
}

# Select which factor set to use based on CRYPTO_MODE
import os as _os
if _os.environ.get("CRYPTO_MODE", "").lower() == "true":
    _BASE_FACTORS = CRYPTO_20
    _ALL_FACTORS = CRYPTO_ALPHA
else:
    _BASE_FACTORS = ALPHA20
    _ALL_FACTORS = ALPHA158

def get_base_factors() -> dict:
    """Return the base feature dict for the current market mode."""
    return dict(_BASE_FACTORS)

def get_all_factors() -> dict:
    """Return the full factor dict for the current market mode."""
    return dict(_ALL_FACTORS)


def validate_qlib_features(expressions: list[str]) -> bool:
    """Validate that Qlib expressions are computable (requires Qlib conda env)."""
    # This is a stub; actual validation requires Qlib in a conda environment
    return True
