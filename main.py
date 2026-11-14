#!/usr/bin/env python3
"""btc-cent-forecast-01: forecast Bitcoin's price 240 minutes after a checkpoint.

Method (backtested on the kit's six practice cases plus 336 pseudo-cases cut
from the same 72-hour windows — see README.md for the numbers):

  1. Take the checkpoint close L (the last price in the case).
  2. Spike-trim L: clamp it into [median60 - 6*MAD60, median60 + 6*MAD60].
     The pool's price is one Orca Whirlpool's own quote, and the rules note an
     unusually large trade moves it "for a moment". A checkpoint close caught
     mid-spike is not the level the price reverts to; the trim caps that.
  3. Shrink 25% toward the mean of the last 240 closes (4 hours):
         forecast = T + 0.25 * (mean240 - T)
     The 4-hour-ahead close is a near random walk, so the honest median is
     close to the current level — but the last close carries the pool's
     microstructure noise, and a little shrinkage toward the recent mean
     trades a small bias for a real variance reduction. On 336 pseudo-cases
     this beats plain persistence by ~2.5% (MAE $388 vs $398); trend
     extrapolation in either direction loses, so no trend term is used.
  4. Round to the grid's 5 decimals and clamp inside (0, 10,000,000).

Deterministic: pure function of the case file, no randomness, no clock, no
network, standard library only. Two runs on the same input write identical
bytes. Never crashes on a case: any unexpected shape falls back to the
checkpoint close (persistence), which is always a valid guess.
"""

import json
import os
import statistics
import sys

INPUT_DIR = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

MIN_PRICE = 0.00001
MAX_PRICE = 9_999_999.99999

# Shrinkage toward the 4-hour mean (see module docstring).
SHRINK = 0.25
MEAN_WINDOW = 240          # minutes of closes averaged for the anchor level
TRIM_WINDOW = 60           # minutes used for the spike trim
TRIM_K = 6.0               # MAD multiples for the trim band


def price5(x):
    """x kept on the grid's 5 decimals and inside the scorer's (0, 10_000_000)."""
    if not isinstance(x, (int, float)) or x != x or x in (float("inf"), float("-inf")):
        raise ValueError("not a finite number")
    return round(min(MAX_PRICE, max(MIN_PRICE, float(x))) * 1e5) / 1e5


def forecast(prices):
    """One 240-minute-ahead price guess from a list of 1-minute closes."""
    if not prices:
        raise ValueError("no prices")
    # Drop any non-finite closes first: one bad value must not poison the
    # median, the mean, or the checkpoint close.
    clean = [float(p) for p in prices
             if isinstance(p, (int, float)) and p == p
             and p not in (float("inf"), float("-inf"))]
    if not clean:
        raise ValueError("no finite prices")
    last = clean[-1]

    # 1-2. Spike trim against the last hour's median +/- 6*MAD.
    window = clean[-TRIM_WINDOW:]
    med = statistics.median(window)
    devs = sorted(abs(p - med) for p in window)
    mad = devs[len(devs) // 2]
    if mad > 0:
        lo = med - TRIM_K * mad
        hi = med + TRIM_K * mad
        trimmed = min(max(last, lo), hi)
    else:
        trimmed = last

    # 3. Shrink 25% toward the 4-hour mean.
    mean240 = sum(clean[-MEAN_WINDOW:]) / min(len(clean), MEAN_WINDOW)
    guess = trimmed + SHRINK * (mean240 - trimmed)
    return price5(guess)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    inputs = sorted(f for f in os.listdir(INPUT_DIR) if f.endswith(".in"))
    for name in inputs:
        case_id = name[: -len(".in")]
        path = os.path.join(INPUT_DIR, name)
        try:
            with open(path, "r", encoding="utf-8") as fh:
                case = json.load(fh)
            markets = case["markets"]
            if not isinstance(markets, list) or len(markets) != 1:
                raise ValueError("case does not hold exactly one market")
            prices = markets[0]["prices"]
            if not isinstance(prices, list) or not prices:
                raise ValueError("market has no prices")
            guess = forecast(prices)
        except Exception:
            # Never leave a case invalid: fall back to the checkpoint close.
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    case = json.load(fh)
                guess = price5(float(case["markets"][0]["prices"][-1]))
            except Exception:
                # No usable price at all; emit a positive placeholder guess.
                guess = price5(1.0)
        out = {"forecasts": [{"case": case_id, "price": guess}]}
        with open(os.path.join(OUTPUT_DIR, case_id + ".out"), "w", encoding="utf-8") as fh:
            fh.write(json.dumps(out) + "\n")


if __name__ == "__main__":
    main()
