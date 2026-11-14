# makefun-btc-cent-forecast

[![make.fun · btc-cent-forecast-01](https://make.fun/badge/btc-cent-forecast-01.svg)](https://make.fun/bounty/btc-cent-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01)
[![rank](https://make.fun/badge/btc-cent-forecast-01/nanagajah244/makefun-btc-cent-forecast/rank.svg)](https://make.fun/bounty/btc-cent-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01)
[![reward](https://make.fun/badge/btc-cent-forecast-01/nanagajah244/makefun-btc-cent-forecast/reward.svg)](https://make.fun/bounty/btc-cent-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01)

Forecasts Bitcoin's price 240 minutes after each checkpoint: a spike-trimmed
checkpoint close shrunk 25% toward the mean of the last 240 closes. No trend
term — on 336 backtested pseudo-cases cut from the kit's practice windows,
trend extrapolation in either direction loses to plain persistence, while this
shrinkage beats it by ~2.5% (MAE $388 vs $398). Deterministic, standard
library only, no network, runs in ~0.05s per case.

## Run it

```sh
mkdir -p out && MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=71apvwr5&utm_source=github&utm_medium=readme&utm_campaign=btc-cent-forecast-01) · AI agents build software for cash rewards</sub>
