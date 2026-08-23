# Pre-Registration Protocol

**Study title:** Do intrusion detection results survive label correction? A matched-flow re-evaluation of CICIDS2017

**Version:** 1.0
**Written:** before any data was loaded or inspected
**Status:** frozen. Any change after data contact must be recorded in `PROTOCOL_AMENDMENTS.md` with a date and a reason.

---

## 1. Why this protocol exists

The single most common way a benchmark-audit paper is rejected is that the reviewer suspects the analysis was tuned until an interesting result appeared. Writing the hypotheses, the metrics and the decision rules down *before* looking at the data removes that objection, and it costs nothing.

Read this document fully before running notebook `01`. Notebook `00` does not touch data and may be run first.

---

## 2. Background

CICIDS2017 (Sharafaldin, Lashkari & Ghorbani, 2018) is the most widely used flow-based intrusion detection benchmark. Three independent groups have since documented errors in it:

- **Engelen, Rimmer & Joosen (IEEE SPW/WTMC 2021)** — errors in traffic generation, flow construction, feature extraction and labelling. They released a fixed CICFlowMeter and a regenerated dataset. Over 20% of original traces were reconstructed or relabelled.
- **Liu, Engelen, Lynar, Essam & Joosen (IEEE CNS 2022)** — extended the audit to CSE-CIC-IDS2018 and released the "improved" CSVs used in this study.
- **Lanvin, Gimenez, Han, Majorczyk, Mé & Totel (CRiSIS 2022)** — independently found packet misordering, duplicate flows, capture gaps and labelling errors.

Despite this, papers reporting 99%+ accuracy on the *original* CICIDS2017 continue to be published. The gap between "the benchmark is known to be broken" and "the field keeps using it" is the space this study occupies.

## 3. The confound that defines the design

The improved dataset was **regenerated from the raw PCAP files with a fixed CICFlowMeter**. TCP flow termination now requires a mutual FIN exchange, and RST packets terminate flows. Flow boundaries therefore moved. The improved data is **not** the original rows with corrected labels.

This means a naive "train on original, train on improved, compare accuracy" study measures three things at once and can attribute none of them:

1. label corrections,
2. flow reconstruction,
3. feature extraction fixes.

We therefore run two arms.

**Arm A — dataset-level.** Train and evaluate on each dataset version separately. Reports the *total* effect a practitioner would experience by switching. Honest, but confounded, and labelled as such throughout.

**Arm B — matched-flow subset.** Join the two versions on `(Src IP, Src Port, Dst IP, Dst Port, Protocol, Timestamp)`. Restrict to flows present in both with identical feature-defining boundaries. On that subset the *only* thing that differs is the label. This isolates the pure label-correction effect and is the contribution of the paper.

Arm B is the reason this study is publishable rather than a lab exercise. If Arm B cannot be built (match rate too low — see gate G2), the paper becomes a report on why the two versions are not comparable, which is still a finding, and the framing changes accordingly.

## 4. Hypotheses

Each is stated so that it can come back false.

- **H1 (headline).** Classifier performance reported on the original CICIDS2017 is inflated relative to the improved version. Specifically, macro-F1 on the original exceeds macro-F1 on the improved dataset under an identical pipeline.
  *Falsified if* the improved dataset yields equal or higher macro-F1.

- **H2 (isolation).** On the matched-flow subset, relabelling alone accounts for a majority of the Arm A gap.
  *Falsified if* the matched-subset gap is under half the Arm A gap, which would mean flow reconstruction — not labelling — drives the difference.

- **H3 (attempted-label sensitivity).** The treatment of `Attempted` flows materially changes reported performance. The spread in macro-F1 across the three policies (→ attack, → benign, dropped) exceeds 0.01.
  *Falsified if* the three policies agree to within 0.01.

- **H4 (equivalence, the boring outcome).** Per-class recall for the classes with no corrected labels is unchanged between versions, within a TOST equivalence margin of ±0.02.
  This one is *expected to hold*. It is included as a positive control: if untouched classes also shift, something in the pipeline is wrong, not the data.

## 5. Data

| Version | Source | Files |
|---|---|---|
| Original | CIC / UNB `GeneratedLabelledFlows` → `TrafficLabelling_` | 8 CSVs, Mon–Fri |
| Improved | Kaggle `ernie55ernie/improved-cicids2017-and-csecicids2018`, dir `CICIDS2017_improved` | monday.csv … friday.csv |

**Mandatory:** use `GeneratedLabelledFlows / TrafficLabelling_`, **not** `MachineLearningCVE`. The latter drops Source IP, Destination IP and Flow ID, which makes the Arm B match key impossible to construct. This is the single most likely way to waste three weeks on this project.

SHA-256 of every downloaded file is recorded in `results/checksums.csv` at download time and never recomputed silently.

## 6. Preprocessing (fixed in advance)

Applied identically to both versions:

1. Strip whitespace from column names; harmonise the two naming schemes via the mapping in `config.py`.
2. Drop identifier columns from the feature matrix: Flow ID, Src/Dst IP, Timestamp, and the row index. Ports and Protocol are **kept** (documented as a known shortcut risk, reported in limitations).
3. Replace ±inf with NaN; drop rows with any NaN in the feature matrix; record how many were dropped per version.
4. Drop constant columns; record which.
5. **Exact-duplicate handling is a reported step, not a silent one.** Count duplicates in each version, then deduplicate. Both the with- and without-duplicate results are reported for the primary configuration.
6. No scaling for tree models. Standardisation fitted on train only for logistic regression.

## 7. Splits

Two protocols, both reported:

- **Random 70/30**, stratified — because this is what the literature does, and the comparison is the point.
- **Day-ordered** — train Mon–Wed, test Thu–Fri — because it is the defensible one. Thresholds and any tuning use a validation slice carved from the training days only.

Test data is touched exactly once per configuration, at the end.

## 8. Models

Logistic regression, random forest, XGBoost. Default or lightly specified hyperparameters, **identical across dataset versions**. No per-version tuning — tuning would reintroduce the confound this design exists to remove.

Seeds: `11, 23, 37, 51, 73`. Every configuration runs all five.

## 9. Metrics

Primary: **macro-F1** (chosen in advance; accuracy is unusable at this class imbalance and is reported only for comparability with prior work).

Secondary: per-class precision/recall/F1, balanced accuracy, MCC, confusion matrices.

Reported as mean ± SD across the five seeds. Never a single run.

## 10. Statistics

- Paired comparisons across seeds: **Wilcoxon signed-rank**, two-sided, α = 0.05.
- Effect size: **Cliff's δ**, reported alongside every p-value.
- Multiple comparisons across the configuration grid: **Holm correction**, applied within each hypothesis family.
- H4 equivalence: **TOST** at ±0.02.
- With five seeds the minimum attainable Wilcoxon p is 0.0625, so **no single per-seed comparison can reach α = 0.05**. This is acknowledged in advance. Where significance is claimed it is on the pooled configuration grid, not on five seeds; otherwise magnitude and consistency of direction are reported instead of significance theatre. Do not increase the seed count after seeing results to manufacture significance.

## 11. Gates

Checked in order. A failed gate changes the paper; it does not get quietly ignored.

- **G1 — integrity.** Both versions load, row counts match the published figures within 1%. Reference: Engelen's erratum gives 9,103 Attempted labels and 1,657,069 Benign flows. If our counts disagree, stop and find out why before proceeding.
- **G2 — match rate.** Arm B requires ≥ 20% of original flows to match an improved flow. Below that, Arm B is dropped and the paper is reframed as an incomparability result.
- **G3 — positive control.** H4 must hold. If untouched classes shift by more than the equivalence margin, the pipeline is at fault, not the data. Debug before reporting anything.
- **G4 — reproducibility.** Re-running notebook `04` in a fresh Colab session reproduces every headline number to within 0.02 absolute. Cross-session drift beyond that is disclosed in the paper.

## 12. Deliberately out of scope

- Deep architectures. This is a data-quality study; adding a CNN-LSTM would invite the reviewer question "did you tune it fairly per version?" and there is no good answer.
- Any claim about which correction is *correct*. We report what changes. Adjudicating Engelen vs Lanvin against ground truth requires the PCAPs and is a different paper.
- CSE-CIC-IDS2018. Same method, second dataset, obvious extension — keep it for the journal version.

## 13. Reporting commitments

- Every number in the manuscript comes from a CSV in `results/`, regenerated by the notebooks. No number is typed in by hand.
- Negative and null results are reported with the same prominence as positive ones. If H1 is falsified, that is the paper's headline.
- A limitations section names: the shortcut risk from retaining ports, the single-benchmark scope, the absence of PCAP-level verification, and the seed-count limit on statistical power.

---

## Sign-off

Signed by all project members before notebook `01` is run:

| Name | Role | Date |
|---|---|---|
| | | |
| | | |

Guide: _______________________  Date: __________
