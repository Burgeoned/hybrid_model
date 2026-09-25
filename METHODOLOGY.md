# methodology

the question is: **among men who lift and run, how many can bench 225 AND run a
sub-19:00 5K?**

the naive answer is to multiply the two odds. that assumes strength and speed are
unrelated. they aren't -- but the evidence pulls in two directions. body mass helps the
bench and costs you on the run, which pushes them apart. general fitness makes people
better at both, which pulls them together. no study measures which wins for bench and 5K
in the same people, so this model reports the answer under each and does not pick one.

this document covers where that correlation comes from, how we modeled the joint
distribution, what the research actually says, and where we're theorizing vs citing.

---

## the reference class -- read this first

**revised 2026-09-15.** this model previously asked "how many people worldwide can do
both" and answered it by multiplying the joint probability by a 4.1B world population.
that was wrong, and wrong by roughly 45x.

the bench marginal below is the `sbd_final` **gym-goer** distribution. the run marginal is the
parkrun **runner** distribution. those are two different reference populations. the
bivariate normal treats them as two coordinates on one person, which means every
probability in this document is *already conditional* on belonging to both -- on being
one of the men who both lift and run regularly. that group is of order 10-25M, not 4.1B.

the sanity check that settled it:

```
p_joint x 4.1B                          =  9.74M "hybrids worldwide"
men who can bench 225 at all (sbd_final)= 10.28M
-> the model claimed 95% of everyone who can bench 225 also runs sub-19
```

**so the model reports a conditional and never a count.** producing a worldwide count
would require the size of the lift-and-run intersection, which is a second unmeasured
parameter stacked on top of rho -- and stacking two unmeasured parameters is where a
model stops being a model. the count is out of scope, deliberately.

> **every number in this document is conditional on: men who both lift and run
> regularly.** not all men. not everyone on earth.

---

## the interference effect -- what the research says

the idea that strength and endurance training interfere with each other goes back to
Hickson (1980), who found that training for both simultaneously produced worse strength
gains than training for strength alone. that paper set off decades of research.

**what's well established:**

- concurrent training reduces hypertrophy compared to resistance-only training.
  Wilson et al. (2012) meta-analysis across 21 studies (J Strength Cond Res 26(8)):
  effect size for hypertrophy was 0.02 for concurrent vs 0.20 for resistance-only.
  that's roughly a 10x reduction in muscle growth rate when you add endurance work.

- running economy degrades with added body mass. the relationship is roughly linear:
  Di Prampero et al. (1986) established that the energy cost of running scales with
  total body mass. carrying more mass = more metabolic cost per unit distance.
  estimates range from 0.8-1.2% increase in oxygen cost per 1% increase in body mass
  (Daniels, 1985; running economy literature broadly).

- serious strength athletes are slower runners, serious endurance athletes are weaker.
  this is directionally obvious but the population-level correlation is not published
  anywhere we found.

**what's not established:**

- there is no peer-reviewed study that measures the correlation between bench press 1RM
  and 5K time in a representative adult population at scale. the literature on concurrent
  training focuses on training outcomes (how much does adding running hurt your bench gains?),
  not on the cross-sectional correlation between current bench and current run time in
  the general gym-going / running population.

- CrossFit Games data has paired lifts and conditioning scores, but it's a massively
  self-selected population (elite competitors). the correlation structure there
  (probably weaker interference, because crossfitters specifically train both) would
  not generalize to the broader gym-going / running public.

- Hyrox results pair run + functional fitness but no barbell bench. no clean dataset
  currently exists that pairs 5K time and barbell bench on the same individuals at
  anything close to population scale.

---

## the rho assumption -- two forces, winner unknown

**revised 2026-09-20.** the earlier version of this section claimed a defensible range of
rho = 0.20-0.40 with a baseline of 0.30, and used a military study as its "lower bound."
a source check found that study points the *other* way. the range and baseline are
withdrawn. what the evidence actually supports is below.

rho is the correlation between log(bench) and log(5K time) among men who both lift and
run. positive rho means stronger men tend to be slower. negative means stronger men tend
to be faster. **the two datasets cannot estimate it** -- the bench marginal and the run
marginal come from different people, and no person appears in both. the running data
also records no bodyweight, which is the variable that links the two. so rho has to come
from outside studies, and those studies point in both directions.

**force 1 -- mass pulls them apart (positive rho).**

**citation corrected 2026-09-23.** this paper was cited as "Treff et al." in every earlier
version of this doc and on screen in the reel. the actual paper is Herrmann FR, Graf C,
Karsegard VL, Mareschal J, Achamrah N, Delsoglio M, Pichard C, Genton L, *Nutrition*
2019;61:1-7 (PMID 30677531). the finding and the numbers were verified and are unchanged;
only the author attribution was wrong.

- Herrmann et al. (2019), *Nutrition*: 1,771 men and 1,353 women at an annual timed city
  run in Geneva, 1999-2016, body composition by **bioelectrical impedance** (an earlier
  draft of this doc said DEXA -- that was wrong). in men, a fat-free mass index in the top
  quartile (>20 kg/m²) was associated with poor running performance, r = -0.50. note
  that this describes the most-muscular quarter, not a straight-line trend across all
  runners. body composition explained 29.8% of the variance in men's running speed.
- PMC8997733 (2022): **30** well-trained young men, DXA. bench 1RM correlated with
  *upper-limb* fat-free mass. an earlier draft quoted r ≈ 0.67-0.74 for "fat-free mass";
  the exact values have not been re-verified against the paper, and the measure is
  upper-limb FFM, not the whole-body FFMI Herrmann used.
- mechanism: the energy cost of running scales with body mass (Di Prampero 1986). more
  muscle to carry, more cost per kilometre.

chaining bench -> FFM -> run speed by multiplying the correlations gives roughly 0.3.
that chain is weak in three ways: it links two different body-composition measures,
it treats a top-quartile association as a linear correlation, and multiplying
correlations is only valid if body composition is the *entire* link between the two.

**force 2 -- general fitness pulls them together (negative rho).**

- Acevedo, Zeigler & Melton (2024), *Int J Exerc Sci* 17(4):429-437 (PMID 38665860):
  64 ROTC cadets (50 men, 14 women). VO2max
  correlated with max trap-bar deadlift r = +0.253 and with the 2-mile run r = +0.612.
  ACFT events are scored in **points** (higher = better), so both correlations mean the
  same thing: cadets with a bigger aerobic engine deadlifted more *and* ran faster.
  chained through VO2max, that implies stronger cadets were slightly *faster*,
  rho ≈ -0.15 on our scale.
- **correction:** an earlier draft chained these as 0.25 x 0.61 = +0.15 and called it
  the lower bound on a positive rho. the sign was wrong. this study is evidence *against*
  the hybrid tax, not a floor under it.
- caveats on this one too: trap-bar deadlift not bench, a fitness-selected population
  that trains both on purpose, and pooled sexes (men are stronger *and* faster, which
  inflates any correlation that pools them).

**what that leaves.** the mass mechanism is real and measured. the fitness mechanism is
real and measured. no study measures their net effect on bench 1RM vs 5K time in the
same people. the honest model therefore reports **scenarios**, not a point estimate:

| scenario | rho |
|---|---|
| fitness wins | -0.15 |
| unrelated -- just multiply | 0.00 |
| size wins | +0.30 |

the sweep in the notebook covers -0.30 to +0.50.

**the sign of rho:**

rho is positive in our formulation but the relationship is negative in plain english.
this is a coordinate system choice: we model bench in lbs (higher = better) and run
time in minutes (lower = better). a positive rho in this coordinate system means
high bench predicts high run time, which is the "slower runner" direction. if you
flip run time to run speed instead, rho would be negative. same relationship, different
sign convention. the math is consistent throughout -- just keep the coordinate system
in mind when reading the covariance matrix.

---

## the bivariate normal model

both bench and run time are log-normally distributed. this means log(bench) and
log(run_time) are normally distributed. the joint distribution of two normals is
a bivariate normal, which has a known CDF.

```python
from scipy.stats import multivariate_normal

mean = [log(bench_median), log(run_median)]
cov  = [[bench_sig**2,              rho * bench_sig * run_sig],
        [rho * bench_sig * run_sig,  run_sig**2              ]]
rv   = multivariate_normal(mean, cov)
```

the quantity we want is P(bench >= target AND run_time <= target):

```
P(bench >= B AND time <= T)
  = P(time <= T) - P(bench < B AND time <= T)
  = p_run - rv.cdf([log(B), log(T)])
```

`rv.cdf([log(B), log(T)])` is the probability that both log(bench) < log(B) AND
log(time) < log(T) simultaneously. subtracting that from P(time <= T) gives the
slice of the run distribution where bench is also above target. this is exact to
machine precision -- no approximation, no sampling error.

**why not Monte Carlo:**

MC is fine for the marginals but fails in the joint tails. for bench 315 + sub-15:35,
even 500,000 trials gave roughly 7 hits. probability estimates based on 7 samples have
enormous Poisson variance -- the 95% CI spans roughly 2x to 0.3x the point estimate.
the bivariate normal gives the exact answer in microseconds.

---

## the headline: how many can do both

**revised 2026-09-22 (v3).** inputs now come from `hybrid_inputs.py` (see "the
distributions used"). spoken numbers are the central estimate; ranges are 95% intervals from
a 20,000-run Monte Carlo over every input that has a range.

among men who both lift and run regularly:

| | central (spoken) | Monte Carlo median | 95% range |
|---|---|---|---|
| bench >= 225 | 1 in 7 | 1 in 7 | 1 in 5 to 1 in 11 |
| 5K <= 19:00 | 1 in 13 | 1 in 13 | 1 in 10 to 1 in 22 |
| **both, fitness wins** (rho -0.15) | **1 in 65** | 1 in 66 | 1 in 41 to 1 in 118 |
| **both, just multiply** (rho 0) | **~1 in 100** | 1 in 100 | 1 in 59 to 1 in 192 |
| **both, size wins** (rho +0.30) | **1 in 320** | 1 in 329 | 1 in 162 to 1 in 800 |

**headline: somewhere between 1 in 65 and 1 in 320 men who lift and run can bench 225 and
run sub-19. multiplying gives about 1 in 100, which is only right if the two forces cancel.**

**threshold: 19:00** (changed from Part 1's 19:03 on 2026-09-22). 19:03 came from Part 1's
rarity matching, which this model doesn't use, and "break 19" on camera should mean exactly
what was computed.

**the status claim, stated carefully:** "doing both is rarer than either alone" is true by
definition (a joint probability can't exceed either marginal), so it isn't a finding. the
finding is the magnitude: even in the fitness-wins scenario, doing both (1 in 65) is ~5x
rarer than sub-19 alone (1 in 13).

two kinds of uncertainty, kept separate on purpose: the *scenarios* are the unmeasured rho
(which force wins); the *95% ranges* are the input uncertainty inside each scenario. the rho
uncertainty is the bigger of the two.

## why this doesn't contradict Part 1

Part 1 found bench 225 and sub-19:03 "equally rare." it compared **worldwide counts**:

| | pool (men) | share | count |
|---|---|---|---|
| lifters who bench | 104M | 1 in 12 | 8.9M bench 225 |
| regular runners | 92M | 1 in 13 | 7.0M sub-19 |

worldwide the pools are nearly the same size *and* the shares nearly match, which is why
count-matching landed on ~9M each.

this model asks a narrower question: the share **within** each sport, with the bench side
restricted to North America, Europe and Oceania (where parkrun's runners are). those
regions lift more and bench heavier, so bench 225 goes from 1 in 12 worldwide to 1 in 7
there, while the run share is unchanged at 1 in 13. same data, different question -- not a
correction of Part 1.

### a population-base bug in run_model

`bench_model` states its regional populations are **16-70** and "validated to sum to UN 2024
world 16-70 estimate (~4,674M)". `run_model` took those same numbers and multiplied by an
adult fraction *again* (North America: 210M x 0.53 = 111M), so its populations are ~0.55x
what they should be and sum to 2,503M instead of 4,674M.

consequences, and what was done about them (**run_model is now fixed, 2026-09-23**):

- **shares are unaffected** -- 1 in 7 and 1 in 13 don't depend on population size.
- **Part 1's worldwide counts were understated by ~1.9x**, and its count-matching with them.
  the fix replaced the regional populations with `bench_model`'s verbatim, moved the
  denominator to 4,674M (16-70), switched the bench counts to `sbd_final` per CLAUDE.md §2,
  and made the equivalence a computed scan instead of hardcoded chart labels.

### answering the Part 1 complaint: "sub-19 is way harder than bench 225"

this was the main pushback on Part 1, and it mostly came from men who bench 225. both
things are true at once, and the reason is this episode's thesis.

**1. the complaint is evidence for the size force.** the people saying it are lifters.
they are heavier than the runners the parkrun distribution describes. at equal aerobic
fitness, a heavier man runs slower -- which is exactly the mechanism that makes "both"
rarer than multiplication predicts.

**2. it is quantifiable.** Cureton & Sparling measured it with weighted vests: each 1% of
added body mass cost ~0.68% of 12-minute-run distance (1.0% on time to exhaustion). from
OpenPowerlifting, men who bench 215-235 in meets have a median bodyweight of **175 lb**;
men benching 225+ median **198 lb**. applying the penalty to a 19:00 engine:

| bodyweight | 5K for the same engine |
|---|---|
| 165 lb (reference runner) | 19:00 |
| 175 lb (median man who benches exactly 225) | 19:47 |
| 198 lb (median man who benches 225+) | **21:33** |

so a man who benches 225+ needs an engine ~2.5 minutes better than a 165 lb runner's to
post the same 5K. "sub-19 is way harder for me" is **correct**, and the model agrees --
that gap is the size force, in seconds.

caveat: Cureton's subjects carried dead weight in a vest. muscle is not pure dead weight.
but bench-press muscle is chest, delts and arms, which is close to dead weight for running,
so the direction is right and the magnitude is plausible for this specific case.
`bodyweight_penalty.py` runs the numbers and draws `05_bodyweight_penalty.png`.

**3. the reference points check out.** sub-19 is not an elite time in the running world:

| population | share breaking 19:00 |
|---|---|
| road-race finishers (men) | ~38% |
| parkrun (men) | ~7% |
| a high-school varsity XC boy | routinely -- a typical varsity 1-7 spans ~16:15-18:30 |

the high-school figures are from coaching forums and running blogs, **not a dataset** --
indicative only. if that line gets used on camera, source it from MileSplit or Athletic.net
first. the road-race and parkrun figures come from this model and Part 1.

**the honest summary:** among *men who run regularly*, 1 in 13 break 19 -- it's a
club-runner standard, not an elite one. among *men who bench 225*, it's much harder,
because they're carrying 20-30 lb more. both statements are in the model.

## the count this model does report

| | |
|---|---|
| men 16-70, N. America + Europe + Oceania | 342M |
| lifters who bench | 45M |
| regular runners | 46M |
| both sports | 6M (independent habits) to 18M (3x overlap) |
| can bench 225 **and** break 19 | **19k - 278k** |

reported only as "tens of thousands, not millions". the overlap between lifting and running
habits is not measured anywhere in the portfolio, so a tighter figure would be false
precision.

**Was Part 1's "19:03 = bench 225" wrong?** The arithmetic reproduced (I got 9.13M against
its published 9.21M), but three things were off, and they've now been corrected in
`run_model`:

1. **halved populations** -- an adult fraction applied to figures that were already 16-70.
2. **mixed-sex comparison** -- the bench count is 99.6% men; the runner count included
   ~1.5M women. Barbell bench 225 is a mostly-male movement in the model itself.
3. **stale bench counts** -- it used `bench_world_model`'s 9.27M; `sbd_final` (the source of
   truth) says 10.28M.

corrected, matching men against men: **bench 225 = sub-18:27**, not 19:03. on the original
mixed-sex basis it's sub-18:03. the three errors partly cancelled, which is why the
published figure looked plausible.

| | published | corrected |
|---|---|---|
| bench 225 | 9.27M | 10.28M (`sbd_final`) |
| equivalent 5K, mixed-sex | sub-19:03 | **sub-18:03** |
| equivalent 5K, men vs men | -- | **sub-18:27** |

the softest input in that chain is the female run tail: the model puts ~1.5% of female
regular runners under 19 minutes. our own check (`test_sanity.py`) finds that roughly
consistent with the male-equivalent time after the standard sex gap, so it is defensible,
but it is what made the mixed-sex match fast.

**What this means for this episode:** nothing changes. This model doesn't claim an
equivalence, compares men to men throughout, and uses a clean 19:00.

**superseded:** v2 (2026-09-20) reported 1 in 54 / 80 / 242 from a North-America-only bench
curve and a fixed 26.5 min run median. v1 (2026-09-15) reported "1 in 40" and "at least twice
as rare" (mass-only, withdrawn).

**what would settle it:** a few thousand men reporting a bench 1RM and a 5K time as the
*same person*. that dataset does not exist at any scale. building it is the point of the
episode's CTA.


## the hybrid tax (applies only if size wins)

the tax is the percentage by which the joint probability falls below independence. it is
only a *tax* when rho is positive; under the fitness-wins scenario it is a bonus -- doing
both is *more* common than multiplication predicts (1 in 65 vs 1 in 100).


the tax is the percentage by which the true joint probability falls below the
independence assumption:

```
tax = (P_independent - P_joint) / P_independent
    = (P_bench x P_run - P_joint) / (P_bench x P_run)
```

it is algebraically the same statement as the suppression factor
(`tax = 1 - 1/suppression`) and is kept only because it is the more familiar framing.

**correction, 2026-09-15.** earlier drafts of this document quoted a tax of "roughly
30-35%" at the 225 / sub-19:03 pair. that figure is not what the code produces and never
was. the actual values:

| rho | hybrid tax |
|---|---|
| 0.20 | 48.7% |
| 0.30 | 66.9% |
| 0.40 | 81.0% |

the 30-35% figure is withdrawn. these values are the size-wins side only; under
fitness-wins the "tax" is negative (doing both is more common than multiplication says).

the effect grows with milestone difficulty, because both milestones sit further into
their tails where rho has more leverage. **that is why 315 and 405 do not ship.** across
the fitness-wins to size-wins span (rho -0.15 to +0.30), the answer moves:

| pair | fitness wins | size wins | swing |
|---|---|---|---|
| bench 225 / sub-19:00 | 1 in 65 | 1 in 320 | **5x** |
| bench 315 / sub-15:35 | 1 in 2,252 | 1 in 76,986 | 34x |
| bench 405 / sub-14:50 | 1 in 24,776 | 1 in 3,288,422 | 133x |

(central inputs, v3.)

deeper in both tails the Gaussian copula's zero tail dependence does more and more of
the work, and the log-normal fit is least reliable exactly there. the 315 and 405 pairs
are reportable as *direction*, never as a figure.

---

## the distributions used

**revised 2026-09-22.** both marginals are now traced to the portfolio's own models, and
`hybrid_inputs.py` holds them for both the notebook and the reel renderer.

**bench -- from `sbd_final`, the source of truth for lifts.** `sbd_final`'s gym-goer curve
starts from OpenPowerlifting (4M sanctioned-meet results, one best raw lift per lifter) for
the *shape*, then slides it down to regional gym-goer medians. this model uses its Pool A
bench rows for men in **North America (median 163 lb, range 148-178), Europe (152, 138-166)
and Oceania (158, 143-173)**, weighted by population x lifting rate x bench adoption, with
sigma 0.28-0.38. the earlier versions used only the North America row (163 lb), which
overstated bench 225 (1 in 6 vs 1 in 7).

why those three regions: the running data is parkrun, whose participants are overwhelmingly
in the UK, Ireland, Australia/NZ, North America and the rest of Europe. pairing parkrun runners
with *world* gym-goers (heavy East and South Asia weight) would put two different populations
on the same axes. the world mixture gives bench 225 at 1 in 12 and would roughly double every
"both" figure.

caveat inherited from `sbd_final`: the regional gym medians are that model's softest input
("published gym-strength surveys", slid to match). they are the same numbers Part 1 and the
bench videos already used.

### matching the tiers

both sports have a "serious" dataset and a "normal" one, and the model has to compare like
with like:

| tier | bench 225 | break 19:00 |
|---|---|---|
| serious -- meet competitors / race finishers | 77% | 38% |
| normal -- gym-goers / parkrun | **13.7%** | **7.4%** |

competitor medians: OPL men 282 lbs (sigma 0.313); road-race men 20.5 min (sigma 0.250,
RunRepeat US 5K analysis via `run_model` -- US-skewed, and used here only to show the tier
contrast, never in the joint model).

the two sides get there differently, and conflating them would misdescribe the method:

- **lifting:** no large dataset of normal gym-goers' 1RMs exists, so `sbd_final` takes the
  competitor curve and slides it down to survey-level gym-goer medians. the bench number is
  *derived*.
- **running:** both tiers are published independently, so we simply use the casual one
  (parkrun). nothing is slid. parkrun is *not* an adjusted road-race distribution.

**parkrun's regional skew is the reason the bench side is regionally restricted.** parkrun
participation is dominated by the UK, Ireland and Australia, with North America and the rest
of Europe behind them; its global median is effectively those runners. so the bench marginal
uses the matching `sbd_final` regions rather than the world mixture. it also means neither
number describes, say, a South Asian or Sub-Saharan African practitioner population.

**5K -- from `run_model` (Part 1).** parkrun men's percentiles P10 / P50 / P90 = 20.5 / 26.5 /
37.0 min, fit log-normal (sigma 0.2304). the raw percentile table is not in the repo; the
values are carried from Part 1. the **median is treated as uncertain between 26.5 and 28.5
min**, because the outside anchors lean slower:

- parkrun's all-finisher global average is ~32 min (includes women and walkers)
- Strava's UK male average 5K is 27:16 (Strava users skew keener than parkrun walkers)
- a 2023 study of Scottish parkrun found mean event performance declining over time
  (*IJERPH* 2023, 20(4):3602 -- abstract only; no sex-specific times given)

**the median is used as published (26.5 min).** an earlier v3/v5 carried it as 26.5-28.5,
justified by the anchors above -- that was wrong: the global ~32 min average includes women
and walkers worldwide, while this percentile table is mostly UK/Australian men, so slowing it
double-counted a regional adjustment the table already reflects. only the spread varies
(+-15%, run_model's own range).

**men only**, for both. no usable rho exists for women, and female barbell-bench participation
(~20-32% of female lifters) makes that marginal unstable.

**bench counts for worldwide totals: not used.** the model reports no counts.

---

## caveats and weaknesses

**the reference class is the thing to get right.** this was the failure that forced the
2026-09-15 revision and it is worth stating twice: the two marginals come from two
different populations, so every probability here is conditional on being in both. the
model cannot produce a worldwide count, and any number here that acquires units of
"people" has been misused. say the reference class out loud, every time.


**rho is the biggest unknown -- including its sign.** the mass evidence (Herrmann) implies
roughly +0.3; the fitness evidence (ROTC) implies roughly -0.15. the answer moves from
1 in 65 to 1 in 320 across that span. the model does not claim a hybrid tax exists; it
claims the answer lies in that range and that multiplication is only right if the two
forces cancel.

**the running percentiles are carried, not re-derived.** the 5K distribution comes from
Part 1's parkrun percentiles; the raw table isn't in the repo, so the median is carried as a
26.5-28.5 min range rather than a point. if the original table turns up, pin it and rerun --
it is the single input that moves the answer most.

**the intersection is assumed to look like each parent.** the model gives men who both
lift and run the gym-goer bench distribution and the parkrun time distribution. people
who do both probably bench a bit less than pure lifters and may run slower than pure
runners. that selection effect is unmodelled.

**no dataset pairs bench and 5K at scale.** this is the fundamental limit of the
model. paired data doesn't exist in a form we can use. CrossFit and Hyrox have
partial data but severe selection bias (people who specifically train for both are
not representative of the gym-going / running population). the general-population
correlation between barbell bench and 5K time has not been measured. this is a
genuine gap in the sports science literature.

**the casual gym-goer distribution may understate the interference.** the gym-goer
normative data represents all gym-goers, including people who don't run at all.
among people who actively do both sports, rho might be higher (they've had to make
explicit tradeoffs). among the general population, many people do one and not the
other, which weakens the observed correlation. this cuts both ways, which is why the
model reports scenarios rather than a baseline.

**the Gaussian copula has zero tail dependence.** this is a structural limitation.
the Gaussian copula's dependence erodes to zero as both variables push toward the
extreme tails, even at rho = 0.40. for the bench 405 + sub-14:50 pair (99th+
percentile in both), a Gumbel copula -- which has positive upper-tail dependence --
would be more theoretically appropriate and would likely produce a *lower* hybrid
tax. we use Gaussian because it's tractable and interpretable; Gumbel would be
the next step for anyone stress-testing the tail estimates.

**we're modeling the marginals, not the training interaction.** the bivariate normal
captures where people currently sit on both dimensions. it does not model the
dynamic question: if you train to improve bench, how much does your 5K suffer? that's
the interference effect literature (Hickson 1980, Wilson et al. 2012). our model
asks "how many people are simultaneously in both top tails right now" -- a snapshot,
not a training recommendation.

**log-normal in the tails.** at bench 405 + sub-14:50 we're in the extreme tails
of both distributions, where log-normal fits are least reliable. this compounds
the Gaussian copula limitation above. treat the tail estimates as order-of-magnitude
rather than precise. bench 225 / sub-19:00 is in the 97th-98th percentile and the
log-normal fit is much better grounded there.

**rho is assumed constant across the range.** a constant rho across the whole
bivariate distribution is a structural limitation of the Gaussian copula. in
reality the correlation likely varies: elite hybrid athletes in the top of both
distributions may have weaker interference (they've specifically optimized for
both), while mid-distribution people may show stronger effects. a varying-rho
model would require the paired dataset that doesn't yet exist.

---

## relevant research

these are the papers most relevant to the assumptions in this model. not an exhaustive
review -- a practical reading list for someone who wants to stress-test the rho estimate.

**interference effect (why bench and run fight each other):**
- Hickson RC (1980). Interference of strength development by simultaneously training
  for strength and endurance. Eur J Appl Physiol 45(2-3):255-63. the original paper.
- Wilson JM et al. (2012). Concurrent training: a meta-analysis examining interference
  of aerobic and strength gains. J Strength Cond Res 26(8):2293-307. best meta-analysis.
- Leveritt M et al. (1999). Concurrent strength and endurance training: a review.
  Sports Med 28(6):413-27.
- Murach KA, Bagley JR (2016). Skeletal muscle hypertrophy with concurrent exercise
  training: it takes two to tango. Exerc Sport Sci Rev 44(2):76-82.

**body mass and running economy:**
- Di Prampero PE et al. (1986). The energetics of endurance running. Eur J Appl
  Physiol 55(3):259-66.
- Daniels J (1985). A physiologist's view of running economy. Med Sci Sports
  Exerc 17(3):332-8.
- Fletcher JR et al. (2009). Muscle mechanics and neuromuscular control of locomotion.
  J R Soc Interface 6(33):439-55.

**body composition as the mediating variable (indirect rho evidence):**
- Herrmann FR et al. (2019). Running performance in a timed city run and body composition:
  a cross-sectional study in more than 3,000 runners. Nutrition (2019).
  1,771 men, bioelectrical impedance, Geneva annual city run (not a 5K). body
  composition explained 29.8% of variance in men's running speed; top-quartile FFMI
  (>20 kg/m²) associated with poor performance, r = -0.50. the key study for the mass
  mechanism.
- Herrmann FR et al. (2019). Fat mass index predicts deterioration of running speed.
  PMC6471649. longitudinal companion -- mass gain tracks with speed loss.
- PMC8997733 (2022). 1RM upper-body compound lifts explain ~45-55% of fat-free mass
  variance in trained males (r ≈ 0.67-0.74). the link from bench to body composition.

**upper body strength and running (scoping review):**
- Curovic D et al. (2024). Potential importance of maximal upper body strength for
  high-intensity running and jumping. Sports 12(12):357. PMC11679821.
  screened 4,730 articles; only 7 met inclusion for distance running. upper body
  strength correlates with sprint speed but no studies on 5K or distance running.
  confirms the literature gap.

**military fitness data (evidence for negative rho):**
- PMC11042848 (2024). Maximal aerobic capacity as a predictor of ACFT total score in
  ROTC cadets, Int J Exerc Sci. n = 64 (50 M, 14 F). VO2max x trap-bar deadlift
  r = +0.253; VO2max x 2-mile run r = +0.612, both on ACFT points. implies stronger
  cadets ran slightly faster (rho ≈ -0.15 on our scale). an earlier draft had this
  sign reversed.

**updated concurrent training meta-analyses:**
- Huiberts et al. (2024). Concurrent strength and endurance training meta-analysis.
  VU Amsterdam. interference small in trained males (g ≈ -0.25), negligible in
  females and upper body. more recent and nuanced than Wilson 2012.
- Schumann et al. (2022). No significant hypertrophy differences when frequency/
  volume matched between concurrent and resistance-only training.

**why no direct bench/run correlation paper exists:**
- concurrent training research focuses on training outcomes (does adding running hurt
  bench gains?), not on cross-sectional population correlation.
- CrossFit research uses WOD-specific metrics, not isolated bench 1RM and 5K.
- the best available evidence is the body-composition chain, which implies rho ≈ 0.30-0.40
  for general adults. military data implies lower values (0.15) in fitness-selected groups.

if you know of a study with paired bench 1RM and 5K time data in a non-CrossFit
population, that paper would substantially sharpen the rho estimate. we don't have one.
