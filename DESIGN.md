# hybrid_model — design doc (v5)

## The question

**Among men who lift and run, how many can bench 225 AND run a sub-19 (19:00) 5K?**

## The answer this model gives

| scenario | rho | 1 in N can do both (central) | 95% range |
|---|---|---|---|
| fitness wins | −0.15 | 65 | 41–118 |
| just multiply | 0.00 | ~100 | 59–192 |
| size wins | +0.30 | 320 | 162–800 |

**Somewhere between 1 in 65 and 1 in 320** — even the generous end is ~5× rarer than sub-19 alone. The model does not pick a winner, because the
evidence doesn't.

---

## Why it can't be more precise — the design constraint

1. **Two separate datasets.** Bench comes from a gym-goer distribution, 5K from a
   regular-runner distribution. No person is in both, so the data can't estimate how
   strength and speed relate.
2. **No bodyweight on the running side.** Body mass is the variable that links the two, and
   the running data doesn't record it.
3. **Outside studies disagree on the sign.** Mass pulls the two apart (Herrmann 2019). Fitness
   pulls them together (ROTC/ACFT 2024). Nobody has measured bench vs 5K in the same people.

So rho is reported as scenarios, never as a point estimate.

---

## Change history

**2026-09-22 — v6 (basis C).** Run median fixed back to Part 1's 26.5: the 26.5-28.5 range
was justified by parkrun's global all-finisher average, which includes women and walkers
worldwide, while the percentile table is mostly UK/Australian men — that was double-counting
a regional adjustment. Added a provenance beat to the reel and replaced the CTA with an
UNDER LOAD series sign-off. Result: 1 in 65 / ~100 / 320.

**2026-09-22 — v5 (script review).** Status-led story; threshold 19:00 (was Part 1's
19:03); scenario renamed "mass wins" → "size wins" to match the script; payoff changed from
the tautological "rarer than either alone" to "~5× rarer than sub-19 alone." Result:
1 in 87 / 130 / 480.

**2026-09-22 — v3.** Inputs traced to the portfolio and moved into `hybrid_inputs.py`, which
the notebook and renderer share. Bench now comes from `sbd_final` for the parkrun footprint
(North America, Europe, Oceania) instead of the North America row alone. The run median is
carried as 26.5–28.5 min, because outside anchors lean slower than Part 1's 26.5. Every
input range is Monte Carlo'd (20,000 runs). Result: 1 in 85 / 130 / 470, up from
54 / 80 / 242. v2 assets are in `_archive/v2_na_only/`.

**2026-09-20 — v2.** v1 reported "1 in 13 becomes 1 in 40, at least twice as rare" at a
rho = 0.30 baseline with a 0.20–0.40 "defensible range." A source check found:

- the ROTC study was used as the range's lower bound with its **sign reversed**. ACFT events
  are scored in points, so fitter cadets were stronger *and* faster, which is evidence for
  negative rho.
- Herrmann 2019 used bioelectrical impedance, not DEXA, and its r = −0.50 describes the
  top-muscle quartile rather than a linear trend.
- PMC8997733 is n = 30 and measures upper-limb fat-free mass, not whole-body FFMI.
- the parkrun percentile table and the NSCA 163 lb median could not be traced to an
  original table.

v1 assets are in `_archive/`.

**2026-09-15 — v1.** The original design multiplied the joint probability by a 4.1B world
population. The joint is conditional on being in both reference populations, so that
overstated by ~45x and implied 95% of 225-benchers also run sub-19. Counts were cut
permanently.

---

## Standing rules

- **Shares are the product.** Everything headline is 1-in-N among men who lift and run.
- **One count is allowed, as an order of magnitude.** "Tens of thousands of men in N.
  America, Europe and Oceania" (span 19k-278k). Never a precise figure: it rests on an
  unmeasured overlap between lifting and running habits. Counts use the `sbd_final`
  16-70 population base, not `run_model`'s (which re-applied an adult fraction).
- **The joint is always analytical** (Gaussian copula). MC only varies the inputs and draws pixels.
- **315 and 405 stay out of public content.** Across the same rho span, 225 swings 5x,
  315 swings 34x, 405 swings 133x.
- **Say where the numbers come from.** Bench is OpenPowerlifting via `sbd_final`; 5K is parkrun via Part 1.
- **Male only.** No usable rho for women.

---

## Outputs

| File | What |
|---|---|
| `hybrid_model.ipynb` | the model — scenarios, sweep, robustness |
| `01_scenarios.png` | the headline: three scenarios as 1-in-N |
| `02_hybrid_scatter.png` | joint cloud under fitness-wins vs size-wins |
| `03_rho_sweep.png` | 1-in-N vs rho, −0.30 to +0.50 |
| `04_robustness.png` | why 315/405 don't ship |

## Next step that would actually settle it

Paired data: the same person's bench 1RM and 5K time. The reel's CTA asks for it in the
comments. A few hundred usable pairs would estimate rho directly for self-selected
hybrid athletes. That's biased, but it's the first direct measurement, and it would be
Part 3.
