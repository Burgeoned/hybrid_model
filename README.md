# hybrid_model

**Part 2.** Among men who lift and run, how many can bench 225 **and** run a sub-19 (19:00) 5K?

---

## the short answer

among **men who lift and run regularly**:

| | central | 95% range |
|---|---|---|
| bench 225 | **1 in 7** | 1 in 5 to 1 in 11 |
| sub-19:00 5K | **1 in 13** | 1 in 10 to 1 in 22 |
| both, if you just multiply | **~1 in 100** | 1 in 59 to 1 in 192 |
| both, if fitness wins | **1 in 65** | 1 in 41 to 1 in 118 |
| both, if size wins | **1 in 320** | 1 in 162 to 1 in 800 |

**Somewhere between 1 in 65 and 1 in 320.** Even the generous end is ~5× rarer than sub-19 alone. Multiplying lands in the middle, and it's only
right if the two forces below cancel out exactly.

---

## why there isn't one number

**The two datasets never meet.** The bench distribution is from gym-goers, the 5K
distribution from regular runners. No person is in both, so the data can't say how strength
and speed relate in the same body. The running data also has no bodyweight, which is the
variable that connects them.

**The outside evidence points both ways:**

- **Muscle mass pulls them apart.** Herrmann et al. 2019: 1,771 men at a timed city run in
  Geneva, body composition by bioelectrical impedance. The most-muscular quarter (FFMI
  > 20 kg/m²) ran slowest, r = −0.50.
- **Fitness pulls them together.** ROTC/ACFT study 2024 (PMC11042848): 64 cadets. VO2max
  correlated +0.25 with trap-bar deadlift and +0.61 with 2-mile run, both scored in points.
  Fitter cadets were stronger *and* faster.

No study measures bench 1RM against 5K time in the same people. So the model runs the
correlation (rho) from −0.15 (fitness wins) to +0.30 (size wins) and reports the range.

---

## what's in here

| file | what it is |
|---|---|
| `hybrid_model.ipynb` | the model |
| `METHODOLOGY.md` | full methodology, every study checked, corrections logged |
| `DESIGN.md` | the design contract and change history |
| `REEL_SCRIPT.md` | the shootable script |
| `render_hybrid_anim.py` | renders the seven reel clips |
| `01`–`04_*.png` | working charts |
| `_archive/` | v1 (mass-only) script, notebook, renderer and clips |

---

## method

Both marginals are log-normal, so log(bench) and log(5K time) are jointly normal in log-space.
`scipy.stats.multivariate_normal` gives the joint CDF exactly:

```python
cov = [[b_sig**2,            rho * b_sig * r_sig],
       [rho * b_sig * r_sig, r_sig**2           ]]
rv  = multivariate_normal([log(b_med), log(r_med)], cov)
p_both = p_run - rv.cdf([log(225), log(19.05)])
```

The joint probability is always analytical. Monte Carlo is used for two things only: varying the
inputs within their ranges (for the 95% intervals) and drawing scatter pixels. Sampling the joint
directly starves in the tails.

---

## known limits

- **rho is unmeasured, including its sign.** That's the headline caveat, not a footnote.
- **Inputs come from the portfolio's own models** (`hybrid_inputs.py`): bench from `sbd_final`
  (OpenPowerlifting shape, slid to gym-goer medians for North America, Europe and Oceania),
  5K from Part 1's parkrun percentiles, used as published (male median 26.5 min; only the
  spread is varied).
- **The intersection is assumed to look like each parent.** People who both lift and run
  probably bench less than pure lifters. That's unmodelled.
- **Male only.** 315 and 405 pairs are too rho-sensitive to publish.

## reproduce

`pip install numpy matplotlib scipy` · run the notebook top to bottom.
