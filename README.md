# hybrid_model

**Part 2.** How many people worldwide can bench 225 AND run sub-19:03 at the same time?

The answer is not `P(bench) x P(run)`. That math assumes the two are independent.
They're not -- muscle mass helps bench, slows your 5K. The joint probability is smaller
than independence predicts. We call that gap the **hybrid tax**.

This repo quantifies the tax using an analytical bivariate normal in log-space and
sweeps the key assumption (the correlation rho) to show how robust the finding is.

---

## the short answer

bench 225 alone: ~0.23% of people worldwide  
sub-19:03 alone: ~0.22% of people worldwide  
both simultaneously (rho = 0.40): roughly 30-40% less likely than independence assumes

the exact hybrid count is in the notebook once the PAIRS run times are updated
against sbd_final bench counts (see DESIGN.md and METHODOLOGY.md).

---

## what's in here

| file | what it is |
|---|---|
| `hybrid_model.ipynb` | main notebook -- distributions, bivariate normal, hybrid tax, rho sweep |
| `METHODOLOGY.md` | how the model works, where rho comes from, caveats, research refs |
| `DESIGN.md` | reel structure and next steps for Part 2 production |

---

## the key technical decision

Monte Carlo fails in the joint tails. at bench 315 + sub-15:35, even 500k MC trials
gave ~7 hits -- Poisson variance that wide makes the estimate useless. we switched
to an analytical approach: because both distributions are log-normal, log(bench) and
log(run_time) are jointly normal in log-space. `scipy.stats.multivariate_normal`
gives the exact joint CDF to machine precision.

```python
from scipy.stats import multivariate_normal
mean = [log(bench_median), log(run_median)]
cov  = [[bench_sig**2,              rho * bench_sig * run_sig],
        [rho * bench_sig * run_sig,  run_sig**2              ]]
rv   = multivariate_normal(mean, cov)

# P(bench >= target AND run <= target)
p_joint = p_run - rv.cdf([log(bench_target), log(run_target)])
```

---

## data sources

running distributions: Parkrun 2023 global report (parkrun.com/statistics)  
lifting distributions: NSCA normative data (casual), OpenPowerlifting (competitive)  
bench world counts: sbd_final model (Jul 2026, 10.28M for bench 225)  
population denominator: UN WPP 2022, ages 18-65 (4.1B)  
rho assumption: concurrent training literature -- see METHODOLOGY.md

---

## reproduce

1. `pip install numpy pandas matplotlib scipy`
2. open `hybrid_model.ipynb`, run all cells top to bottom
3. update PAIRS run times against sbd_final counts before final figures (see TODO cell)

---

## part 1

[run_model](https://github.com/Burgeoned/run_model) -- the running equivalent of bench 225.
same methodology, single-sport rarity. sub-19:03 matches bench 225 at 9.2M people worldwide.
