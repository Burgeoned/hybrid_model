# methodology

the question is: how many people can bench 225 AND run sub-19:03 at the same time?

the naive answer is to multiply: P(bench 225) x P(sub-19:03). that assumes independence.
the two are not independent. the same traits that help you bench -- body mass, muscle
cross-section, upper body hypertrophy -- actively hurt your running economy. the joint
probability is smaller than the product of the marginals. how much smaller depends on
the correlation between the two.

this document covers where that correlation comes from, how we modeled the joint
distribution, what the research actually says, and where we're theorizing vs citing.

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

## the rho assumption

we model the relationship as a correlation in log-space: rho = 0.40.

in practical terms: if you bench well above average, your predicted 5K time is
moderately above average (slower). if you run well above average, your predicted
bench is moderately below average. the word "moderately" is rho = 0.40.

**where 0.40 comes from:**

it's an informed estimate, not a measured value. the reasoning chains through body
composition, which is the best-studied mediating variable between the two.

**the body composition chain (best available indirect evidence):**

1. bench press correlates strongly with fat-free mass. a 2022 study (PMC8997733)
   found that 1RM for upper-body compound lifts explained ~45-55% of variance in
   fat-free mass in trained males (r ≈ 0.67-0.74).

2. fat-free mass index (FFMI) negatively predicts running speed. Treff et al. (2019),
   a cross-sectional study of 3,067 recreational runners with DEXA body composition
   measurements, found FFMI in the highest quartile (>20 kg/m²) was associated with
   the slowest times. the body-composition model explained 29.8% of variance in male
   running speed. a companion longitudinal paper (Treff et al., 2019, PMC6471649)
   found that increases in fat mass index predicted deterioration of running speed.

3. chaining these two correlations: bench → FFMI (r ≈ 0.70) × FFMI → run speed
   (r ≈ -0.50 in men) implies a bench-to-run-time correlation of roughly **0.30-0.40**
   via body composition alone. add any direct muscle-mass-to-economy effect and
   the upper bound is around 0.45.

**what other data sources suggest:**

- military data (ROTC cadets, PMC11042848): VO2max correlated with deadlift r = 0.25
  and with 2-mile run r = 0.61. chaining through VO2max as a common factor implies
  a deadlift-to-run-time correlation of roughly 0.25 × 0.61 = **0.15** in that
  fitness-selected population. bench and deadlift track together, so this sets a
  lower bound on the plausible range.

- concurrent training interference (Huiberts et al., 2024 meta-analysis): the
  interference effect on upper body strength is small (g ≈ -0.20 to -0.30 in trained
  males, negligible in females). this means dedicated hybrid athletes can perform
  well at both, which pulls the *observed* cross-sectional correlation down from
  what the body-composition chain alone would predict.

**revised defensible range: 0.20-0.40.**

0.40 is the upper bound supported by the body composition chain. 0.20 is a reasonable
lower bound given the military data and the modest interference effect. we set
rho = 0.40 as the baseline (upper bound), which is conservative in the direction of
overstating the hybrid tax. the rho sweep covers 0.10-0.70; the highlighted
plausible range in the chart is 0.20-0.40.

this is the weakest part of the model. we're working from indirect chains, not
measured data. no peer-reviewed study directly pairs bench press 1RM with 5K time.
the rho sweep is the honest answer to that uncertainty.

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

## the hybrid tax

the hybrid tax is the percentage by which the true joint probability falls below
the independence assumption:

```
tax = (P_independent - P_joint) / P_independent
    = (P_bench x P_run - P_joint) / (P_bench x P_run)
```

at rho = 0.40 and the bench 225 / sub-19:03 milestone pair, the tax is roughly 30-35%.
meaning: if independence were true, you'd expect ~X people. with the negative
correlation, you actually get ~0.65X to 0.70X people.

the tax increases with milestone difficulty. bench 405 + sub-14:50 has a larger tax
than bench 225 + sub-19:03, because both milestones sit further in their respective
tails, where the correlation has more leverage. extreme outliers in one trait are
increasingly unlikely to be extreme outliers in the negatively correlated trait.

---

## the distributions used

**running:** same Parkrun 2023 parameters as run_model.
- male: median 26.5 min, sigma 0.2304
- female: median 31.5 min, sigma 0.2328

**bench (casual gym-goer):** NSCA normative data, north america.
- male: median 163 lbs, sigma 0.33
- female: median 83 lbs, sigma 0.345

for the joint model we use the male casual distributions as the primary basis, because:
- the bench/run tradeoff is most meaningful in the casual practitioner population
  (competitive powerlifters rarely run; elite runners rarely powerlift)
- the interference literature is mostly studied in recreationally trained men
- the female bench fraction issue (only 20-32% of female gym-goers do barbell bench)
  makes the female joint distribution harder to model cleanly

this is a simplification. a full gender-specific joint model would need separate rho
estimates for male and female populations, which don't exist in the literature.

**bench counts for worldwide totals:** sbd_final (Jul 2026 refresh).
- bench 225: 10.28M
- bench 315: 1.18M
- bench 405: 0.135M

these are the updated numbers from the most recent combined model. run_model shipped
with 9.27M for bench 225 (from bench_world_model). for hybrid_model, use sbd_final.
the run equivalents in PAIRS need to be re-matched against the higher sbd_final counts
before the hybrid joint numbers are final.

---

## caveats and weaknesses

**rho is the biggest unknown.** everything else in this model -- the log-normal
assumption, the distributions, the bivariate normal structure -- is well-grounded
in theory and data. the correlation coefficient is not. we estimated it from
indirect evidence: the body-composition chain implies 0.30-0.40; military fitness
data implies a lower bound around 0.15. the plausible range is 0.20-0.40. the rho
sweep covers 0.10-0.70 and the finding that the hybrid tax is real and meaningful
is robust across the full range. the exact percentage is not.

**no dataset pairs bench and 5K at scale.** this is the fundamental limit of the
model. paired data doesn't exist in a form we can use. CrossFit and Hyrox have
partial data but severe selection bias (people who specifically train for both are
not representative of the gym-going / running population). the general-population
correlation between barbell bench and 5K time has not been measured. this is a
genuine gap in the sports science literature.

**the casual gym-goer distribution may understate the interference.** the NSCA
normative data represents all gym-goers, including people who don't run at all.
among people who actively do both sports, rho might be higher (they've had to make
explicit tradeoffs). among the general population, many people do one and not the
other, which weakens the observed correlation. rho = 0.40 as the upper bound is
the conservative assumption -- it errs toward overstating the hybrid tax.

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
rather than precise. bench 225 / sub-19:03 is in the 97th-98th percentile and the
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
- Treff M et al. (2019). Running performance in a timed city run and body composition:
  a cross-sectional study in more than 3,000 runners. Nutrition (2019).
  FFMI explains 29.8% of variance in male running speed; Q4 FFMI associated with
  slowest times. the key study linking fat-free mass to 5K performance.
- Treff M et al. (2019). Fat mass index predicts deterioration of running speed.
  PMC6471649. longitudinal companion -- mass gain tracks with speed loss.
- PMC8997733 (2022). 1RM upper-body compound lifts explain ~45-55% of fat-free mass
  variance in trained males (r ≈ 0.67-0.74). the link from bench to body composition.

**upper body strength and running (scoping review):**
- Curovic D et al. (2024). Potential importance of maximal upper body strength for
  high-intensity running and jumping. Sports 12(12):357. PMC11679821.
  screened 4,730 articles; only 7 met inclusion for distance running. upper body
  strength correlates with sprint speed but no studies on 5K or distance running.
  confirms the literature gap.

**military fitness data (lower bound on rho):**
- PMC11042848 (2024). VO2max as predictor of ACFT total score in ROTC cadets.
  VO2max x deadlift r = 0.25; VO2max x 2-mile run r = 0.61. implies deadlift-to-run
  correlation of ~0.15 via VO2max. sets the lower bound of the plausible rho range.

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
