# Repository selection options: 15 quantified combinations

`funnel.md` explains why the corpus fits in 60 repositories: a cap
(`max_repos = 60`) reached inside the "found by ≥ 2 channels" group. This
file answers the next question — *if the cap is raised, on what criterion is
the list cut?* Fifteen combinations are evaluated on the **1,187 distinct
candidates** of `manifest/discovery.jsonl`, with the full GitHub metadata
(`manifest/repo_stats.jsonl`).

To reproduce: `python scripts/fetch_repo_stats.py` then
`python scripts/selection_options.py [--markdown]`.

## The criteria tested

All can be evaluated **before cloning**. They read as a ladder: each
`B`*n* row adds a criterion to the previous one; `A1`–`A3` are alternative
forms, not tightenings of the ladder.

- **alive**: accessible (11 candidates return 404), not a *fork*, not
  archived, neither mirror, nor template, nor empty;
- **Python present / substantial / majority**: ≥ 1 byte, ≥ 10 kB (≈ 250
  lines), ≥ 50% of the repository's bytes. This criterion alone rules out,
  without cloning, false positives such as `gnames/gnverifier`, a Go project
  that came in through the seed list;
- **tracked / established repository**: ≥ 10 then ≥ 50 commits on the
  default branch;
- **reasonable size**: 50 kB ≤ `diskUsage` ≤ 200 MB — below that it is a
  toy, above it is a data warehouse (the biggest current repository,
  `biopragmatics/bioregistry`, weighs 1.6 GB by itself);
- **neither course nor vendored library**: the name, description or
  *topics* contain `curso`, `course`, `tutorial`, `exercise`, `homework`,
  `práctica`, `workshop`…; or the repository is named like the library
  (`rdflib`, `rdfextras`, `sparqlwrapper`, `isodate`);
- **declared / extractable licence**: an explicit SPDX licence, then a
  licence listed in `snippet_licences` — it is what decides whether an
  excerpt can enter the published examples;
- **activity**: last commit ≥ 2020, then ≥ 2023;
- **visibility**: ≥ 1 star;
- **attestation**: found by ≥ 2 discovery channels, or published on PyPI
  with a declared dependency on rdflib (Wheelodex channel), or describing
  itself as an RDF project (`rdf`, `sparql`, `ontolog*`, `shacl`, `skos`,
  `knowledge graph`… in the name, the description or the *topics*);
- **cap per organisation**: at most *k* repositories from a single GitHub
  account — this is what would have prevented five repositories of a single
  course from weighing 65% of the census.

## Results, by decreasing number of repositories

| option | criteria | repositories | extractable | self-described RDF | ★ med. | commits med. | active ≥ 2023 | orgs (max) | disk | of the 60 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **B0 baseline** | accessible, not fork, not archived/mirror/template/empty, ≥ 1 byte of Python | **1130** | 591 | 537 | 2 | 56 | 69% | 936 (27) | 98.9 GB | 59/60 |
| **B1 substantial Python** | B0 + ≥ 10 kB of Python (≈ 250 lines) | **1021** | 548 | 472 | 3 | 70 | 72% | 856 (23) | 98.1 GB | 52/60 |
| **B2 tracked repository** | B1 + ≥ 10 commits | **847** | 497 | 408 | 4 | 109 | 71% | 704 (23) | 86.2 GB | 50/60 |
| **B3 reasonable size** | B2 + 50 kB ≤ size ≤ 200 MB (neither toy nor data warehouse) | **744** | 450 | 371 | 4 | 109 | 70% | 624 (23) | 18.3 GB | 44/60 |
| **B4 neither course nor vendored library** | B3 + exclusion of teaching material and of repositories named like the library | **723** | 445 | 358 | 5 | 108 | 71% | 613 (20) | 17.1 GB | 40/60 |
| **B5 declared licence** | B4 + an explicit SPDX licence | **449** | 445 | 243 | 7 | 129 | 75% | 383 (8) | 8.6 GB | 29/60 |
| **B6 extractable licence** | B4 + licence allowing the republication of excerpts (`snippet_licences`) | **445** | 445 | 243 | 7 | 129 | 75% | 379 (8) | 8.6 GB | 28/60 |
| **B7 alive since 2020** | B6 + last commit ≥ 2020-01-01 | **401** | 401 | 225 | 6 | 129 | 83% | 338 (8) | 7.9 GB | 24/60 |
| **B8 majority Python** | B7 + Python ≥ 50% of the repository's bytes | **337** | 337 | 196 | 7 | 121 | 83% | 287 (8) | 6.1 GB | 23/60 |
| **B9 established project** | B8 + ≥ 50 commits | **249** | 249 | 144 | 10 | 232 | 86% | 217 (5) | 5.3 GB | 22/60 |
| **A3 avowed RDF, 2 per organisation** | B4 + extractable licence + the project describes itself as RDF + cap of 2 repositories per organisation | **232** | 232 | 232 | 10 | 115 | 80% | 209 (2) | 4.3 GB | 19/60 |
| **B10 seen by someone** | B9 + ≥ 1 star | **216** | 216 | 134 | 14 | 238 | 85% | 191 (5) | 4.3 GB | 22/60 |
| **B11 active since 2023** | B10 + last commit ≥ 2023-01-01 | **184** | 184 | 117 | 16 | 266 | 100% | 163 (4) | 4.0 GB | 20/60 |
| **A2 declared rdflib dependency** | B4 + PyPI distribution declaring rdflib (Wheelodex channel) | **87** | 69 | 29 | 2 | 122 | 92% | 80 (4) | 1.1 GB | 7/60 |
| **A1 attested by 2 channels** | B4 + found by ≥ 2 independent discovery channels | **52** | 35 | 36 | 23 | 218 | 71% | 43 (9) | 0.9 GB | 34/60 |

Columns: *extractable* = licence allowing an excerpt to be republished;
*self-described RDF* = the project describes itself as an RDF project;
*orgs (max)* = number of distinct GitHub accounts, and number of
repositories of the most represented account; *disk* = sum of GitHub
`diskUsage`; *of the 60* = how many of the 60 current repositories the
criterion would keep.

The real disk usage is about **1.6 times** this estimate: the 60 current
repositories total 5.7 GB of `diskUsage` for 9.0 GB on disk (shallow clone +
working copy). Count ≈ 45 GB for B3, ≈ 8.5 GB for B9. At 97 Python files per
repository on average (median 45), B9 would give of the order of **24,000
analysed files** against 5,812 today.

## What the figures say

**The pool exists.** 1,130 candidates out of 1,187 pass the baseline. The
60-repository corpus is not an availability constraint: it is an arbitrary
cap, and the only physical constraint — disk — is settled by the size
criterion (98.9 GB → 18.3 GB when excluding data warehouses, without losing
one repository in six).

**Licence is the real bottleneck, and it costs 38%.** Going from B4 (723) to
B5 (449) eliminates 274 repositories with no explicit licence. Today the
consequence is heavy: 698 of the corpus's 1,557 RDF files (45%) are
ineligible for the sample for this reason. Selecting on licence from the
outset gives a corpus of which **100% of the files can be sampled** — 249
repositories in B9, all extractable, against 37 out of 60 today.

**The current corpus ≈ "attested by 2 channels" (A1, 52 repositories).**
This is exactly what the ranking of `select` produced, and it explains the
profile: a median of 23 stars, but only 35 extractable repositories out of
52 and a strong concentration (up to 9 repositories from a single account).
Cross-attestation is a good signal of relevance, a bad criterion of volume.

**PyPI (A2, 87) is the purest criterion but the narrowest**: a declared
dependency on rdflib in a published distribution is proof of use, not a
heuristic. But 87 repositories, and a median of 2 stars — many small
distributions. To be kept as a *stratum*, not as a filter.

**The per-organisation cap costs little and protects a lot**: A3 keeps 232
repositories with at most 2 per account, against 20 for a single account in
B4. It is the structural guarantee that a statistical study demands — the
files of a single project are not independent observations.

## Decision, and what it gave

**Maxime chose B7, on 2026-08-28.** The exact criteria and the second,
post-analysis stage are recorded in `funnel.md` § 3.

Realised figures, to compare with the 401 repositories forecast by the table
above: **444 repositories in the manifest** (the 60 of wave 1 are kept, 384
added), of which **407 satisfy the criteria** and **376 survive the
post-analysis pruning**. The gap with the forecast comes from three
adjustments made when implementing the criteria: archived repositories
remain admitted (`exclude_archived = false`, inherited from wave 1), the
teaching marker is searched at the start of a word and not as a substring
("course" is in "discourse"), and the list of "copies of the library" was
reduced to rdflib and its forks — pySHACL and OWL-RL are *clients* of
rdflib, hence exactly the code that the study targets.

Measured result: 38,845 Python files analysed, 6,095 RDF-relevant, 182,664
RDF operations, 22 GB on disk. The forecast announced ≈ 32,000 files and
≈ 12.5 GB; the overshoot comes from the wave-1 repositories kept and from a
few voluminous projects under the 200 MB cap.

The recommendation that follows is the one that was formulated before the
decision; it is kept as it was.

## Recommendation (before the decision)

**B9 (249 repositories)**, with a cap of 3 repositories per organisation
applied afterwards. Rationale: all extractable (so the whole corpus can be
sampled, which is not the case today), a median of 232 commits and 10 stars
(real projects, not trial repositories), 86% active since 2023, ≈ 8.5 GB on
disk and ≈ 24,000 files to analyse — the analyser processes 5,812 files in a
few minutes, the factor of 4 is painless.

If one wants to aim wider without losing quality, **B7 (401)** is the best
compromise: the same licence and activity guarantees, without the popularity
and Python-proportion thresholds which are choices of taste rather than
validity criteria.

If, on the contrary, one wants a stratum that is defensible for a
generalisation argument, **A3 (232)** is the only option where *every*
repository declares itself an RDF project and where no account weighs more
than two repositories.

## What these criteria cannot do

Two decisive exclusions can only be evaluated **after** cloning and
analysis, and must form a second stage:

1. **No relevant Python file** — `min_rdf_files`. On the current corpus, 53
   repositories out of 60 (88%) have at least one RDF file, but this corpus
   is biased by the seed list; on a broad pool, count rather on 70–85%. B9
   (249) would therefore give of the order of **175 to 210 useful
   repositories**.
2. **Third-party library vendored in the tree** — the case of
   `MKLab-ITI/prophet`, which supplied 44 of the 141 validated pairs without
   any of them being application code (see `funnel.md` § 5.1). No GitHub
   metadata flags it: only the directory tree reveals it.

## The objection not to be sidestepped

Widening the corpus does not mechanically increase the study's statistical
power. **The unit of analysis is not the repository, it is the validated
pair**, and the bottleneck is neither discovery nor cloning: it is the human
review of the translations — 151 regions reviewed by hand consumed an entire
session and a model's quota. Going from 60 to 249 repositories without
touching the sampling quotas (12/16/24 files per band) would produce exactly
the same number of pairs, drawn from a more diverse pool: **a better corpus,
not better statistics**.

What would improve the statistics, in order:

1. **raise the sampling quotas** and industrialise the review — that is where
   the *n* is gained;
2. **cap per repository and per organisation** in the sample, so that the
   pairs are roughly independent: today 141 pairs come from 16 repositories,
   three of which supply 103 (prophet 44, nanopub-py 34, pyLODE 25) — and
   prophet's 44 are vendored rdflib;
3. **only then** widen the corpus, which then serves to feed higher quotas
   without re-drawing the same projects.

In other words, B9 is the right corpus *provided that* it comes with a rise
in quotas; otherwise it only changes the method sentence.
