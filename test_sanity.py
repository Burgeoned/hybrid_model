"""Sanity checks for hybrid_model. Run: python test_sanity.py

No pytest dependency on purpose - plain asserts and a printed report.

Three kinds of check:
  MATH   - invariants that must hold or the model is broken
  INTERNAL - the model agreeing with itself (central vs Monte Carlo, rounding)
  EXTERNAL - agreement with the portfolio's other models and with outside anchors

EXTERNAL failures don't always mean this model is wrong; they can mean two models
disagree. Those print as WARN with the discrepancy spelled out, because at least
one known cross-model conflict is real (see the population-base check).
"""
from __future__ import annotations

import os

import numpy as np
from scipy.stats import lognorm, norm

from hybrid_inputs import (BENCH_SIG, FOOTPRINT, RUN_MEDIAN, RUN_SIG0, SCENARIOS,
                           B_TGT, R_TGT, central, monte_carlo, p_both, spoken)

FM = 0.504
PASS, WARN, FAIL = [], [], []


def check(name, ok, detail=""):
    (PASS if ok else FAIL).append(name)
    print(f'  {"PASS" if ok else "FAIL"}  {name}{"  -- " + detail if detail else ""}')


def warn_if(name, ok, detail=""):
    if ok:
        PASS.append(name); print(f'  PASS  {name}')
    else:
        WARN.append(name); print(f'  WARN  {name}  -- {detail}')


pb, pr = central()

# ── MATH ──────────────────────────────────────────────────────────────────
print("\nMATH INVARIANTS")
for rho, name in SCENARIOS:
    pj = p_both(pb, pr, rho)
    check(f"[{name}] probability in [0,1]", 0 <= pj <= 1, f"{pj:.6f}")
    # Frechet bounds: a joint can never exceed either marginal, nor fall below
    # the overlap forced by the marginals summing past 1.
    check(f"[{name}] respects Frechet bounds",
          max(0.0, pb + pr - 1) - 1e-12 <= pj <= min(pb, pr) + 1e-12,
          f"{max(0.0, pb + pr - 1):.6f} <= {pj:.6f} <= {min(pb, pr):.6f}")

check("rho = 0 reproduces plain multiplication",
      abs(p_both(pb, pr, 0.0) - pb * pr) < 1e-9,
      f"{p_both(pb, pr, 0.0):.8f} vs {pb * pr:.8f}")

js = [p_both(pb, pr, r) for r in np.linspace(-0.5, 0.6, 23)]
check("joint falls monotonically as rho rises", all(np.diff(js) < 0))

check("'both' is always rarer than either alone",
      all(p_both(pb, pr, r) < min(pb, pr) for r, _ in SCENARIOS),
      "true by definition - this is why the reel quotes a magnitude, not this fact")

# ── INTERNAL ──────────────────────────────────────────────────────────────
print("\nINTERNAL CONSISTENCY")
mc_pb, mc_pr = monte_carlo(n=4000, seed=1)
warn_if("central bench share sits inside the MC spread",
        np.percentile(mc_pb, 2.5) <= pb <= np.percentile(mc_pb, 97.5),
        f"central {pb:.4f} vs MC {np.percentile(mc_pb, 2.5):.4f}-{np.percentile(mc_pb, 97.5):.4f}")
warn_if("central run share sits inside the MC spread",
        np.percentile(mc_pr, 2.5) <= pr <= np.percentile(mc_pr, 97.5),
        f"central {pr:.4f} vs MC {np.percentile(mc_pr, 2.5):.4f}-{np.percentile(mc_pr, 97.5):.4f}")
warn_if("central and MC median agree within 10%",
        abs(np.median(1 / mc_pb) - 1 / pb) / (1 / pb) < 0.10,
        f"1 in {1/pb:.1f} central vs 1 in {np.median(1/mc_pb):.1f} MC")

check("run median is fixed (no leftover 26.5-28.5 range)", RUN_MEDIAN[0] == RUN_MEDIAN[1],
      f"{RUN_MEDIAN}")
# Assert on the model's own values, not literals: spoken() inherits Python's
# round-half-to-even, so spoken(13.5) is 14 while the model's 13.47 gives 13.
_said = (spoken(1 / pb), spoken(1 / pr),
         spoken(1 / p_both(pb, pr, SCENARIOS[0][0])),
         spoken(1 / p_both(pb, pr, SCENARIOS[2][0])))
check("spoken numbers match the script", _said == (7, 13, 65, 320), f"{_said}")

# ── EXTERNAL: the portfolio's other models ────────────────────────────────
print("\nEXTERNAL: cross-model")
# bench_model/sbd_final regional populations are stated as 16-70 and validated to
# sum to UN's 4,674M. run_model once applied an adult fraction to those same numbers
# a SECOND time, halving every runner pool; fixed 2026-09-23. This reads run_model's
# live table so the bug can't come back unnoticed.
SBD_POP = {"North America": 210, "Europe": 450, "Oceania": 19}


def _run_model_pops():
    import json, re
    nb = json.load(open(os.path.join("..", "run_model", "run_world_model.ipynb"),
                        encoding="utf-8"))
    src = "".join("".join(c["source"]) for c in nb["cells"] if "REGIONS = [" in "".join(c["source"]))
    return {name: float(pop) for name, pop in
            re.findall(r"\('([^']+)',\s*([\d.]+),\s*0\.", src)}


try:
    RUN_POP = _run_model_pops()
    shared = {k: RUN_POP[k] for k in SBD_POP if k in RUN_POP}
    ratio = sum(shared.values()) / sum(SBD_POP[k] for k in shared)
    warn_if("run_model uses the same population base as sbd_final", abs(ratio - 1) < 0.02,
            f"run_model pops are {ratio:.2f}x sbd_final's for {sorted(shared)} - "
            f"an adult fraction applied to an already-16-70 base. Shares are unaffected, "
            f"counts are not.")
except Exception as exc:                       # run_model not checked out alongside
    warn_if("run_model population base readable", False, f"could not read run_model: {exc}")

for r in FOOTPRINT:
    check(f"[{r.name}] uses the sbd_final population",
          r.pop_m == SBD_POP[r.name], f"{r.pop_m}M vs {SBD_POP[r.name]}M")

# our footprint share must exceed the world share: these are the heavy-bench regions
W = [(210, .22, .78, 163), (450, .15, .74, 152), (165, .10, .72, 148), (950, .07, .60, 128),
     (380, .08, .74, 133), (310, .05, .66, 133), (1080, .025, .60, 113), (500, .035, .62, 118),
     (610, .015, .60, 118), (19, .20, .75, 158)]
w = np.array([p * l * a for p, l, a, _ in W]); w = w / w.sum()
world_pb = float((w * (1 - lognorm.cdf(B_TGT, float(np.mean(BENCH_SIG)),
                                       scale=np.array([m for *_, m in W])))).sum())
check("footprint bench share exceeds the world share", pb > world_pb,
      f"footprint 1 in {1/pb:.1f} vs world 1 in {1/world_pb:.1f}")

# ── EXTERNAL: outside anchors ─────────────────────────────────────────────
print("\nEXTERNAL: outside anchors")
grid = np.linspace(20, 600, 20000)
cdf = sum(wi * lognorm.cdf(grid, float(np.mean(BENCH_SIG)), scale=r.male_median[0])
          for wi, r in zip(np.array([r.pop_m * r.lift_rate[0] * r.male_adopt for r in FOOTPRINT]) /
                           sum(r.pop_m * r.lift_rate[0] * r.male_adopt for r in FOOTPRINT), FOOTPRINT))
gym_med = float(np.interp(0.5, cdf, grid))
warn_if("gym-goer bench median is plausible (140-185 lb)", 140 <= gym_med <= 185, f"{gym_med:.0f} lb")
warn_if("bench 225 share is plausible (8-20% of male benchers)", 0.08 <= pb <= 0.20, f"{100*pb:.1f}%")
warn_if("sub-19 share is plausible (3-12% of male runners)", 0.03 <= pr <= 0.12, f"{100*pr:.1f}%")

# ── WOMEN ─────────────────────────────────────────────────────────────────
print("\nWOMEN")
FEM = [(210, .22, .32, 83), (450, .15, .28, 78), (19, .20, .30, 80)]   # sbd_final female rows
wf = np.array([p * l * a for p, l, a, _ in FEM]); wf = wf / wf.sum()
pb_f = float((wf * (1 - lognorm.cdf(B_TGT, 0.345,
                                    scale=np.array([m for *_, m in FEM])))).sum())
f_sig = (np.log(44.5) - np.log(24.5)) / (2 * norm.ppf(0.90))
pr_f = float(norm.cdf((np.log(R_TGT) - np.log(31.5)) / f_sig))
print(f'  women: bench 225 = {100*pb_f:.3f}% of female benchers | sub-19 = {100*pr_f:.2f}% of female runners')

check("female bench 225 share is far below male", pb_f < pb / 20, f"{100*pb_f:.3f}% vs {100*pb:.1f}%")

# A sub-19 for a woman should be about as rare as a men's time ~11% faster
# (the standing sex gap in distance running). If the female tail were well
# calibrated these two would land close.
GAP = 0.11
male_equiv = float(norm.cdf((np.log(R_TGT * (1 - GAP)) - np.log(RUN_MEDIAN[0])) / RUN_SIG0))
warn_if("female sub-19 tail is calibrated against the male-equivalent time",
        0.5 <= pr_f / male_equiv <= 2.0,
        f"women {100*pr_f:.2f}% vs men at {R_TGT*(1-GAP):.1f} min {100*male_equiv:.2f}% "
        f"(ratio {pr_f/male_equiv:.2f}) - the female run tail is the softest input in "
        f"either model; Part 1's count-matching leans on it")

# ── COUNTS (the number the reel now quotes) ───────────────────────────────
print("\nCOUNTS  (16-70 base, men, N.America + Europe + Oceania)")
pop_m = sum(r.pop_m for r in FOOTPRINT) * FM
lifters = sum(r.pop_m * r.lift_rate[0] * r.male_adopt for r in FOOTPRINT) * FM
runners = sum(p * x for p, x in [(210, .12), (450, .14), (19, .16)]) * FM
print(f'  men 16-70 {pop_m:.0f}M | lifters-who-bench {lifters:.0f}M ({100*lifters/pop_m:.0f}%) '
      f'| regular runners {runners:.0f}M ({100*runners/pop_m:.0f}%)')
check("lifter pool below the male population", lifters < pop_m)
check("runner pool below the male population", runners < pop_m)
warn_if("participation rates are plausible (5-30% each)",
        0.05 < lifters / pop_m < 0.30 and 0.05 < runners / pop_m < 0.30)

lo_hi = []
for k in (1.0, 3.0):                     # habit overlap: independent .. 3x
    both_sports = min(lifters * runners / pop_m * k, runners)
    for rho, _ in (SCENARIOS[0], SCENARIOS[2]):
        lo_hi.append(both_sports * p_both(pb, pr, rho) * 1e6)
print(f'  men who can do both: {min(lo_hi):,.0f} to {max(lo_hi):,.0f}  '
      f'(overlap 1x-3x x rho scenarios)')
check("count never exceeds the bench-capable population", max(lo_hi) < lifters * pb * 1e6)
check("count never exceeds the sub-19 population", max(lo_hi) < runners * pr * 1e6)

print(f'\n{len(PASS)} passed, {len(WARN)} warned, {len(FAIL)} failed')
if WARN:
    print('WARNINGS: ' + '; '.join(WARN))
if FAIL:
    raise SystemExit('FAILED: ' + '; '.join(FAIL))
