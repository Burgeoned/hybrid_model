"""Single source for hybrid_model's inputs, central estimate and Monte Carlo.

Imported by hybrid_model.ipynb and render_hybrid_anim.py so the notebook and the
reel can't disagree about a number.

Provenance:
- Bench: sbd_final Pool A gym-goer table (men), limited to the regions the
  running data comes from. sbd_final's curve is OpenPowerlifting's shape slid
  down to regional gym-goer medians; it is the portfolio's source of truth for
  lifts (CLAUDE.md §2).
- 5K: run_model (Part 1) parkrun percentiles, male P10/P50/P90 = 20.5/26.5/37.0,
  used as-is. Only the spread is varied (+-15%, run_model's own range).
- rho: scenarios, not an estimate. See METHODOLOGY.md.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import lognorm, norm
from scipy.stats import multivariate_normal as mvn


@dataclass(frozen=True)
class Region:
    name: str
    pop_m: float                              # 16-70 population, millions
    lift_rate: tuple[float, float, float]     # mode, lo, hi
    male_adopt: float                         # share of male lifters who bench
    male_median: tuple[float, float, float]   # bench median lbs: mode, lo, hi


# Verbatim from sbd_final Pool A 'Bench' rows. Parkrun's footprint is UK/Ireland,
# Australia/NZ, North America and the rest of Europe, so these three regions -
# pairing world gym-goers with parkrun runners would mix two different places.
FOOTPRINT: tuple[Region, ...] = (
    Region('North America', 210, (0.22, 0.17, 0.28), 0.78, (163, 148, 178)),
    Region('Europe',        450, (0.15, 0.10, 0.20), 0.74, (152, 138, 166)),
    Region('Oceania',        19, (0.20, 0.16, 0.25), 0.75, (158, 143, 173)),
)
BENCH_SIG = (0.28, 0.38)                 # sbd_final SIG_A_M

RUN_P10, RUN_P90 = 20.5, 37.0
# Fixed at Part 1's 26.5 as of 2026-09-22. An earlier version carried 26.5-28.5,
# justified by parkrun's ~32 min all-finisher global average - but that figure includes
# women and walkers worldwide, while this percentile table is mostly UK/Australian men.
# Slowing it was double-counting a regional adjustment the table already reflects.
RUN_MEDIAN = (26.5, 26.5)                # run_model (Part 1), fixed
RUN_SIG0 = (np.log(RUN_P90) - np.log(RUN_P10)) / (2 * norm.ppf(0.90))
RUN_SIG_SPREAD = 0.15                    # run_model's own +-15%

# 19:00, not Part 1's 19:03: 19:03 came from rarity-matching, which this episode doesn't
# use, and "break 19" should mean exactly what was computed.
B_TGT, R_TGT = 225, 19.0                 # bench 225 lbs / 5K 19:00
SCENARIOS: tuple[tuple[float, str], ...] = (
    (-0.15, 'fitness wins'), (0.0, 'just multiply'), (0.30, 'size wins'))


def p_bench_ge(b: float, medians: np.ndarray, weights: np.ndarray, sig: float) -> float:
    w = weights / weights.sum()
    return float((w * (1 - lognorm.cdf(b, sig, scale=medians))).sum())


def p_run_le(t: float, median: float, sig: float) -> float:
    return float(norm.cdf(np.log(t), np.log(median), sig))


def p_both(pb: float, pr: float, rho: float) -> float:
    """P(bench >= B and 5K <= T) under a Gaussian copula.

    Exact for log-normal marginals, and still valid for the bench mixture, which
    is not log-normal. Positive rho = stronger men tend to be slower.
    """
    zb, zr = norm.ppf(1 - pb), norm.ppf(pr)
    return float(pr - mvn([0, 0], [[1, rho], [rho, 1]]).cdf([zb, zr]))


def central(b: float = B_TGT, t: float = R_TGT) -> tuple[float, float]:
    """Every input at its mode / midpoint. The spoken numbers come from here."""
    meds = np.array([r.male_median[0] for r in FOOTPRINT], dtype=float)
    w = np.array([r.pop_m * r.lift_rate[0] * r.male_adopt for r in FOOTPRINT])
    pb = p_bench_ge(b, meds, w, float(np.mean(BENCH_SIG)))
    pr = p_run_le(t, float(np.mean(RUN_MEDIAN)), RUN_SIG0)
    return pb, pr


def monte_carlo(n: int = 20_000, seed: int = 42,
                b: float = B_TGT, t: float = R_TGT) -> tuple[np.ndarray, np.ndarray]:
    """Draw (P(bench), P(5K)) pairs with every input varied inside its range."""
    rng = np.random.default_rng(seed)
    pb, pr = np.empty(n), np.empty(n)
    for i in range(n):
        meds = np.array([rng.triangular(r.male_median[1], r.male_median[0], r.male_median[2])
                         for r in FOOTPRINT])
        w = np.array([r.pop_m * rng.triangular(r.lift_rate[1], r.lift_rate[0], r.lift_rate[2])
                      * r.male_adopt for r in FOOTPRINT])
        pb[i] = p_bench_ge(b, meds, w, rng.uniform(*BENCH_SIG))
        pr[i] = p_run_le(t, rng.uniform(*RUN_MEDIAN),
                         rng.uniform(RUN_SIG0 * (1 - RUN_SIG_SPREAD),
                                     RUN_SIG0 * (1 + RUN_SIG_SPREAD)))
    return pb, pr


def spoken(n: float) -> int:
    """How a 1-in-N is said on camera: exact under 100, nearest 10 above."""
    return int(round(n)) if n < 100 else int(round(n, -1))
