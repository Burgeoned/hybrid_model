# hybrid_model — Part 2 design doc

**The question:** what fraction of people worldwide can bench 225 AND run sub-19:03 at the same time?

**Why it's not just bench × run:**
Muscle mass helps bench, slows your 5K. Endurance training caps strength gains. The two are
negatively correlated — rho ≈ −0.40 in log-space based on sports science literature. So the
joint probability is smaller than independence assumes. That gap is the "hybrid tax."

---

## Foundation already built

`run_model/run_world_model.ipynb` cells `d655dd72` and `5552149d` already contain:
- `exact_joint()` — analytical bivariate normal CDF (no MC starvation in tails)
- `PAIRS` — matched bench/run milestones: 225/19:03, 315/15:35, 405/14:50
- Hexbin scatter + rho sensitivity sweep chart (`07_hybrid_rarity.png`)
- Hybrid tax table printed for all three milestone pairs

Do NOT rewrite this from scratch. Copy those cells into this notebook as the starting point.

---

## Bench counts to use

Use `sbd_final/sbd_final_results.csv` — NOT bench_world_model. run_model used
bench_world_model (9.27M for 225) but sbd_final has been refreshed since:
- bench 225: **10.28M**
- bench 315: **1.18M**
- bench 405: **0.135M**

Re-run the inverse lookup for run equivalents against these updated counts before finalizing.
Run times will shift slightly slower (more people can bench now → need a faster run time to match).

---

## Reel structure (Part 2)

Hook: "bench 225 and run sub-19 at the same time — how many people can actually do both?"

The counterintuitive beat: "not bench_prob × run_prob — they fight each other."
Show the hybrid tax visually: independence bar vs actual joint bar, gap labeled as %.

Visual sequence:
1. Bench curve + run curve side by side (from `10_equivalence_scoreboard.png` as b-roll)
2. Hexbin scatter — zoom into top-left corner where hybrids live
3. Hybrid tax bar chart — one bar "if independent", one bar "actual", gap highlighted
4. Rho sensitivity sweep — shows the answer is robust to the correlation assumption
5. Number reveal: ~X million people worldwide (to be computed with updated sbd_final counts)

Sign-off: "if that's you — you're genuinely one of the rarest combinations of athlete on earth."

---

## Key parameters

- Distribution: log-normal for both, same params as run_model
- Correlation: rho = −0.40 (negative — more muscle = slower 5K)
  - Sensitivity range: −0.25 to −0.55, results robust across this range
- Method: analytical bivariate normal (`scipy.stats.multivariate_normal`)
  - MC starvation is a real problem in the joint tails — do NOT use MC for the estimates
- Denominator: same 4.1B (18-65 population)

---

## Output charts needed

| File | Description |
|---|---|
| `01_hybrid_scatter.png` | Hexbin joint distribution, milestone lines, hybrid region highlighted |
| `02_hybrid_tax.png` | Grouped bars: independent vs joint for 225/315/405 |
| `03_rho_sweep.png` | Joint probability vs rho for bench 225 / sub-19:03 |
| `04_hybrid_reveals.png` | Clean number cards — how many people worldwide per pair |
