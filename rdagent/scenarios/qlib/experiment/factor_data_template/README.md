# How to read files.
For example, if you want to read `filename.h5`
```Python
import pandas as pd
df = pd.read_hdf("filename.h5", key="data")
```
NOTE: **key is always "data" for all hdf5 files **.

# Here is a short description about the data

| Filename       | Description                                                      |
| -------------- | -----------------------------------------------------------------|
| "daily_pv.h5"  | Adjusted daily price and volume data. (In CRYPTO_MODE: data is continuous 7x24, no weekend/holiday gaps, no adjustment factor) |


# For different data, We have some basic knowledge for them

## Daily price and volume data
$open: open price of the instrument on that period.
$close: close price of the instrument on that period.
$high: high price of the instrument on that period.
$low: low price of the instrument on that period.
$volume: volume of the instrument on that period.
$factor: adjustment factor (always 1.0 for crypto — no ex-rights/dividends).
          Raw $close is the actual trading price, no adjustment needed.