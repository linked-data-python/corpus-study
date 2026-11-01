# The corpus funnel: what goes in, what comes out, and why

Reference document. It answers a question that comes up again each time
work resumes — *what does the corpus really represent?* — and it gathers
**all the exclusion criteria**, at every level (repository, file, region,
pair), with what each one removes.

Four stages: **repository** (§ 1), **file** (§ 2), **region** — and there
are two of them, the one for the first draw by density (§ 4, frozen) and the
one for the corpus study by stratum of use (§ 5, living) — then **measured
pair** (§ 5.3).

Repository and file figures: wave 2 of 2026-08-28, B7 criteria,
`config_version` 1.0.0. Figures for the stratified draw and the campaign:
2026-08-29, seed 20260828 (`rdfeval status` regenerates them).
Table per candidate repository:
[`results/summary/candidates.csv`](results/summary/candidates.csv).

---

## 1. Repository level

| step | criterion | where | remaining |
|---|---|---|---:|
| discovery | 4 channels: GitHub code search (728), GitHub repository search (397), Wheelodex `rdflib` (121), seed list (20); 75 repositories confirmed by ≥ 2 channels | `rdfeval/discover.py` | **1,187** |
| metadata | licence, languages and bytes, size, dates, commits, *topics*, head SHA, collected in a single GraphQL pass for **all** candidates | `scripts/fetch_repo_stats.py` | 1,187 |
| selection criteria | option B7 (§ 3), applied candidate by candidate | `rdfeval/criteria.py` | −743 excluded |
| manifest | the 60 wave-1 repositories are **kept** even though they no longer satisfy the criteria — reviewed translations depend on them | `rdfeval/select.py` | **444** |
| acquisition | `--depth 1` clone at the pinned commit, 8 in parallel | `rdfeval/acquire.py` | 444 cloned, 22 GB |

Exclusion reasons, per candidate (a candidate can accumulate several):

| reason | repositories |
|---|---:|
| no licence declared | 460 |
| fewer than 10 commits | 234 |
| no commit since 2020 | 196 |
| less than 10 kB of Python | 114 |
| more than 200 MB (data warehouse) | 96 |
| less than 50 kB (toy) | 83 |
| non-redistributable licence (`NOASSERTION`, `MIT-0`, `BSD-3-Clause-Clear`) | 75 |
| teaching material | 31 |
| inaccessible repository (404) | 11 |
| *fork* | 9 |
| the repository **is** the library (`rdflib`, `rdfextras`, `rdflib-rdfstar`) | 4 |
| mirror or template | 2 |

The first filter is the **licence**: 535 candidates out of 1,187 have no
licence allowing an excerpt to be republished. This is the price of a corpus
in which 100% of the files can be sampled — wave 1 had 37 out of 60, and 698
of its 1,557 RDF files (45%) were ineligible for that reason alone.

### What the ranking did, and no longer does

In wave 1, `select` sorted by `(not a seed, −number of channels, −stars)`
and stopped at `max_repos = 60`. As 20 seeds and 75 multi-channel
repositories already exceeded the cap, the examination stopped **inside the
"≥ 2 channels" group**: 63 repositories examined, **zero** repositories found
by a single channel, and the tie-break by stars never brought a repository
in. The most-starred repository examined had 623, while
`topoteretes/cognee` (30,309 ★), `datahub-project/datahub` (12,601 ★),
`schemaorg/schemaorg` (6,227 ★) stayed out — and `RDFLib/rdflib` itself
(2,499 ★), absent from the seed list.

In wave 2 the cap (`max_repos = 500`) is no longer reached: **the criteria
do the cutting**, not the rank. The 1,104 single-channel candidates were all
examined.

### Renamed and vanished repositories

Five repositories had been renamed upstream (including `oeg-upm/yatter` →
`citiususc/yatter` and `NREL/BuildingMOTIF` → `NatLabRockies/BuildingMOTIF`):
`select` follows the redirect and records the canonical name; the stale
discovery line is folded away. **Eleven** of the 1,187 candidates are
inaccessible today (404 checked on 2026-08-28), including two seeds:
`vemonet/sparql-void-generator`, and `RDFLib/rdflib-endpoint` — which has not
disappeared but was transferred to `vemonet/rdflib-endpoint`, the old path
not redirecting. The seed was stale, not the repository.

## 2. File level

| step | criterion | where | remaining |
|---|---|---|---:|
| initial index | all `.py` files of the clones | `rdfeval/corpus.py` | 58,446 |
| **committed virtual environments** | `exclude_dirs`: `site-packages`, `dist-packages`, `env`, `venv`, `virtualenv`, `build`, `dist`, … | `config/evaluation.toml` | −15,756 together with the size limit |
| **vendored libraries** | `vendored_dirs`: a top-level directory named after a third-party package, **unless it is the repository's own package**; plus any `…/lib/python*/…` tree | `rdfeval/criteria.py` | **−3,845** in 4 repositories |
| size | `max_file_bytes = 1_000_000` | `corpus.py` | **38,845 analysed** |
| unanalysable | 478 Python 2 files — **declared, not silently dropped** | `analyze.py` | 38,845 (of which 478 in error) |
| RDF relevance | ≥ 1 RDF operation detected | `analyze.py` | **6,095** |
| conforming stratum | files of the repositories satisfying the criteria and not pruned | `corpus.py` | **5,190** surface-measured |

The two file-level exclusions are of the same nature — third-party library
code presented as project code — and were found a month apart:

1. **Committed virtualenv** (wave 1, design record
   [401](../corpus/401-plan-etude-corpus.md) § Révision):
   2,549 files, 30% of the initial index, including rdflib itself, counted
   as "real code using rdflib". No sampled file came from them, so the sample
   was kept.
2. **Vendored library outside a virtualenv** (wave 2): 3,845 files in four
   repositories. `MKLab-ITI/prophet` embeds rdflib at its root —
   **all of its 41 RDF-relevant files** are library code;
   `prrvchr/mContactOOo` and `prrvchr/uno` embed an entire Python
   distribution (setuptools, selenium, trio) under `uno/lib/python/`, the
   layout of a virtualenv without the `site-packages` marker.

The exception "the package is the repository's own" is indispensable:
`RDFLib/sparqlwrapper` must keep its `SPARQLWrapper/` directory, which is
its own source code.

## 3. The criteria adopted — option B7

Fifteen combinations were quantified on the 1,187 candidates
([`options_repo_selection.md`](options_repo_selection.md)); **Maxime chose
B7 on 2026-08-28**. It keeps the licence and activity guarantees without the
popularity and Python-proportion thresholds, which are a matter of taste
rather than validity.

**First stage**, decidable on metadata alone, before any cloning
(`stage1_reasons`) — a repository gets in if it satisfies *all* the
criteria:

| criterion | threshold | what it rules out |
|---|---|---|
| accessible | neither 404, nor empty repository | candidates that vanished since discovery |
| not a *fork* | `isFork = false` | copies with no history of their own |
| neither archived, nor mirror, nor template | | skeletons; archived repositories remain admitted |
| substantial Python | ≥ 10 kB (≈ 250 lines) | projects in another language, without cloning |
| tracked repository | ≥ 10 commits | trial repositories |
| reasonable size | 50 kB ≤ `diskUsage` ≤ 200 MB | toys and data warehouses |
| no teaching material | `curso`, `course`, `tutorial`, `exercise`, `homework`, `práctica`, `student`… **at the start of a word** in the name, the description or the *topics* | copies of the same assignment by each student |
| not the library itself | the repository is named `rdflib`, `rdfextras`, `rdflib-rdfstar` | `alcides/rdflib`; **not** pySHACL nor OWL-RL, which are *clients* of rdflib |
| extractable licence | SPDX ∈ `snippet_licences` | anything from which an excerpt cannot be republished |
| alive | last commit ≥ 2020-01-01 | code abandoned before Python 3.8 |

The teaching marker is searched at the **start of a word** and not as a
substring: "course" is inside "discourse". A test checks this.

**Second stage**, after cloning and analysis (`stage2_reason`) — these
criteria need the code:

1. fewer than 2 Python files: **7 repositories**;
2. all the Python is unanalysable (Python 2 project): **1 repository**;
3. no RDF-relevant file: **30 repositories**.

The 38 pruned repositories **stay in the manifest** with their reason in the
`pruned` field: they keep the provenance of the regions and pairs already
reviewed, but leave the census, the surface analysis and the sampling.

### Result

| | wave 1 | wave 2 |
|---|---:|---:|
| repositories in the manifest | 60 | **444** |
| of which satisfying the criteria | 24 | **407** |
| pruned after analysis | — (criteria not applied) | 38 |
| repositories actually measured | 53 | **376** |
| Python files analysed | 5,812 | **38,845** |
| RDF-relevant files | 1,557 | **6,095** |
| RDF operations | 47,323 | **182,664** |
| licence allowing extraction | 37 / 60 | **421 / 444** |
| disk | 9 GB | 22 GB |

The 36 wave-1 repositories that no longer satisfy the criteria are not
removed: they carry `selection_ok: false` and the list of reasons. Four of
them supplied validated pairs (`MKLab-ITI/prophet`,
`maparent/virtuoso-python`, `openphacts/ops-search`,
`lawlesst/vivo-rdflib-sparqlstore`), all ruled out for inactivity since 2018.

## 4. Region level — study 401 (density draw)

**This stage dates from wave 1 and has not been replayed.** The sample was
drawn from the 60 repositories of the time, not from the 376 measured today;
the 151 hand-reviewed translations and the 140 pairs proved equivalent
remain valid as measurements, but their starting population is six times
narrower than the current corpus.

The artefacts concerned, not to be confused with wave-2 data — all carry
their pipeline revision in their `provenance` field:

| artefact | revision | what it describes |
|---|---|---|
| `results/raw/sample.json` | `18d6518` | 52 files drawn from 17 repositories, seed 20260827 |
| `results/raw/regions.jsonl` | `4f2f05f` | 163 regions extracted from these files |
| `examples/<band>/<id>/` | — | 163 folders, of which 151 hand-reviewed translations |
| `results/raw/validation.jsonl` | `e7edab9` | 140 proven equivalences, 1 unresolved |
| `results/raw/pairs.jsonl`, `results/summary/pairs.csv` | `e7edab9` | 141 pairs compared |
| `results/summary/aggregate.json`, `aggregate_bands.csv`, `fig_*.{png,pdf}` | `e7edab9` | statistics and figures derived from these pairs |
| `results/summary/audit.json`, `results/raw/audit_{sample,negatives}.jsonl` | `c43f8ff` | precision 0.99 and miss rate 12%, judged by hand on wave 1 |

Still depending on it, with the same figures:
**`article/tgdk/corpus_study.tex`** — 163 regions, 151 reviewed, 141 pairs,
140 equivalent, median token reduction of 1.1%. This is the only dependency
left: the 24 tasks of `user_study/config/tasks.generated.json` were
**regenerated from 403** (they all carry `"study": "403"`) and no longer
come from here.

Conversely, everything that comes from `analyze` and `surface`
(`files_index.jsonl`, `results/raw/analysis/`, `surface.jsonl`,
`corpus.json`, `surface.json`) carries revision `5db2c56` or later and does
describe the 444 repositories.

These artefacts are **kept**: a sampling wave 2 completes them (`draw_wave`
adds without re-drawing) rather than redoing them, and the translations
already reviewed remain valid.

| step | criterion | remaining |
|---|---|---:|
| sampling | density bands (`< 0.05` / `< 0.20` / `≥ 0.20`), quotas 12 / 16 / 24, cap of 3 files per repository and per band, seed 20260827 | **52 files** (+ 10 control) |
| region extraction | `min_rdf_ops = 2`, `max_region_loc = 120`, `coverage_threshold = 0.5` (otherwise the whole file) | **163 regions** |
| human review | model quota exhausted on the last 12 | **151 reviewed**, 12 not reviewed |
| classification | 108 *directly-expressible*, 25 *minor-restructuring*, 8 *awkward*, 7 *not-expressible*, 3 *excluded* | |
| comparison | the *not-expressible* and *excluded* are not compared | **141 pairs** |
| validation | RDF isomorphism + observable values | **140 equivalent**, 1 unresolved |

> **Open point.** 44 of the 141 pairs (31%) come from files of
> `MKLab-ITI/prophet` that are vendored rdflib
> (`rdflib/extras/infixowl.py`, `rdflib/plugins/sparql/sparql.py`,
> `rdflib/plugins/parsers/pyRdfa/*`). These files have no longer been
> analysed since wave 2, but the pairs still exist and the article counts
> them. The conclusions withstand their removal — inline-construction goes
> from +5.2% to +6.3% in tokens, the AST nodes stay at +10.0%, on 96 pairs
> and 15 repositories instead of 141 and 16 — but a decision is needed:
> remove them, or keep them while declaring them as library code.

## 5. Region level — corpus study (draw by stratum of use)

This is the living stage. It takes nothing from the 401 stage above: a
different population (the 376 measured repositories, not the 60 of wave 1),
a different unit of draw (the usage **site**, not the file), a different
criterion (the **kind of use**, not the density). The two example trees stay
separate (`examples/` versus `examples/`) and their aggregates are never
mixed under a single figure.

### 5.1 From repository to site

| step | criterion | where | remaining |
|---|---|---|---:|
| repositories in the manifest | § 1 | `select.py` | 444 |
| **eligible for the draw** | `snippet_ok` (republishable licence) **and** not pruned | `strata.py` | **385** |
| files of the conforming stratum | § 2 | `corpus.py` | 5,190 |
| **sites** | one located occurrence of a stratum shape, 14 strata | `surface.py` → `results/raw/sites.jsonl` | **29,231** |

Two remarks on these 385, because they cannot be deduced from § 1:

- the draw's pool is filtered on the **licence**, not on the B7 criteria.
  Nine eligible repositories do not satisfy B7 (inactivity, size) and could
  therefore be drawn. **No region came from them** — the gap is latent, not
  realised — but it is there and is worth aligning;
- a single code location is a **site of several strata**: a run of `.add`
  calls in a loop counts for three. The 29,231 sites are therefore not
  29,231 distinct places.

### 5.2 From site to region

`rdfeval strata`, seed **20260828**, target **100 regions per stratum**, cap
**4 per repository and per stratum**.

For each stratum, in order: the stratum's sites are sorted by
`(repository, path, line)` — a stable key, hence reproducible — then shuffled
by `random.Random(20260828)`. The list is traversed up to the target,
skipping a site whose repository already has 4 regions in this stratum, an
unreadable file, and a site whose **enclosing region** cannot be extracted.
The enclosing region is the function that contains the site
(`min_rdf_ops = 2`, `max_region_loc = 120`), or **the whole file** when the
qualifying functions cover less than half of the file's RDF operations
(`coverage_threshold = 0.5`) — extracting a region that hides most of the
RDF work would be misleading.

Two deduplications, and they explain all the gaps in the table:

1. **within a stratum**, two sites of the same region give only one region;
2. **across strata**, a region already drawn is reused and **credited to
   both**: it will be translated once and counted in each.

| stratum | sites | repositories | credited | filed | cap¹ | final² |
|---|---:|---:|---:|---:|---:|---:|
| `ns_import_project` | 1,271 | 65 | 100 | 100 | 260 | 21 |
| `ns_def_local` | 1,061 | 156 | 100 | 100 | 624 | 22 |
| `add_isolated` | 5,053 | 220 | 100 | 98 | 880 | 25 |
| `add_in_loop` | 3,646 | 208 | 100 | 85 | 832 | 24 |
| `add_run_shared_subject` | 1,246 | 154 | 100 | 78 | 616 | 24 |
| `remove` | 636 | 81 | 100 | 94 | 324 | 23 |
| `trav_one_step` | 5,235 | 185 | 100 | 92 | 740 | 23 |
| `trav_navigation` | 1,039 | 99 | 100 | 90 | 396 | 25 |
| `trav_single_value` | 2,252 | 111 | 100 | 76 | 444 | 24 |
| `trav_existence` | 261 | 43 | **89** | 72 | 172 | 23 |
| `sparql_literal` | 884 | 99 | 100 | 95 | 396 | 22 |
| `sparql_interpolated` | 140 | 21 | **53** | 49 | 84 | 23 |
| `bind_initbindings` | 333 | 56 | 100 | 81 | 224 | 25 |
| `coercion_datatype` | 6,174 | 242 | 100 | 86 | 968 | 25 |
| **TOTAL** | **29,231** | — | **1,342** | **1,196** | — | **329** |

¹ theoretical cap = repositories × 4. ² "final" column as of 2026-09-03,
after the complete campaign: it refers to the sample of 350 of § 5.3, not to
the 1,196. "Credited" = regions credited to the stratum; "filed" = regions
**filed** under `examples/<stratum>/`, a multi-stratum region being filed
only once. Hence 1,342 credits for **1,196 distinct regions** — 124 belong
to two or more strata (one to five).

**The two strata under the target are not under it for lack of sites.**
`trav_existence` has 261 sites in 43 repositories (cap 172) and reaches only
89; `sparql_interpolated` has 140 sites in 21 repositories (cap 84) and
reaches only 53. In both cases it is the **number of distinct enclosing
regions** reachable under the cap of 4 that sets the bound, not the
population: several sites fall in the same function. `undrawable_sites` is 0
everywhere — no site was lost to unreadability or to an impossible
extraction.

The draw covers **242 repositories** (out of 385 eligible), with at most 38
regions from a single repository across all strata combined
(`jupyter-naas/abi`, `altunelyusuf/SemanticTechnologies`). 1,152 regions are
functions, 44 are whole files.

### 5.3 From the draw to the final sample: 1,196 → 350

The draw produced 1,196 regions; **the article's sample has 350, exactly 25
per stratum** (Maxime's decision, 2026-09-03). It is a stage of the funnel
in its own right, and it is reproducible.

The rule, which **reproduces the order of `scripts/make_batches.py`** so that
the selection is the same as the one the campaigns followed:

1. strata in alphabetical order;
2. a **single** `Random(20260828)`, shared across the strata — this is what
   the script does, and this is why the order can only be reproduced this
   way;
3. within each stratum, the non-final ones sorted by `sorted()` then
   shuffled by this generator — the shuffled list is the UNFILTERED list, as
   in the script;
4. one takes the first ones of that list until 25 is reached together with
   the final ones, **skipping** the non-final ones classified `excluded` or
   `not-expressible`.

| | regions |
|---|---:|
| drawn | 1,196 |
| **kept** | **350** (14 × 25) |
| of which final | 210 |
| of which drafts to translate | 140 |
| removed | 846 |
| of which non-final `excluded` | 25 |
| of which non-final `not-expressible` | 5 |

**The nineteen FINAL `not-expressible` regions are kept.** They are the
study's negative results — the `@prefix` limit, the query assembled at run
time, the pattern received as data — and not waste. Only the non-final ones
bearing these classifications go, because they have no translation to show.

The measurements do not move by a single figure: all the measured pairs come
from final regions, all of which are kept. Two denominators do change: the
regions attempted are now read out of 350 and not out of 1,196, and coverage
goes from 190/215 to **190/210**, the 25 regions not evaluable in isolation
having left the sample. Their finding remains true and documented; it simply
no longer has support in the tree, only in the git history.

### 5.4 From region to measured pair

Figures of 2026-09-03, on the final sample of 350.

| step | criterion | remaining |
|---|---|---:|
| regions drawn | § 5.2 | 1,196 |
| **retained for the article** | § 5.3 | **350** |
| mechanical draft | written for all of them from the draw on (`materialise = true`) | 350 |
| **attempted** by an agent | campaign closed on 2026-09-03, no eligible draft left | **350** |
| not evaluable in isolation | `excluded`: the driver can run neither the original nor the translation | −21 |
| **translated, status `final`** | translation + driver + proven equivalence | **329** |
| of which not expressible | the language does not reach it — it is a **result**, not a loss | 26 |
| of which awkward | `awkward`: a form exists, it gains nothing | 6 |
| of which expressible | `directly-expressible` (271) + `minor-restructuring` (26) | **297** |
| measured pairs | metrics computed — **to be replayed, 119 finals post-date the last `compare`** | 190 |
| **approved** | human review — **lock: `--force` only returns provisional figures** | **0** |

Expressiveness coverage over what could be evaluated: **297 / 329** (90%).

The 21 regions that remain at `draft` status are exactly the 21 `excluded`
ones: without an executable driver, there is no equivalence to prove. No
stratum therefore reaches 25 finals except four (`add_isolated`,
`bind_initbindings`, `coercion_datatype`, `trav_navigation`); the others top
out between 21 and 24, the pruning of § 5.3 having removed the pool that
would have allowed replacing an `excluded` one.

Of the 190 pairs, the oracle splits into **113 by graph isomorphism** (the
region builds) and **77 by equality of the values produced** (it reads) — it
is this second oracle (design record corpus/405) that lets the reading
regions enter an evaluation.

### 5.5 Is `examples/` obsolete?

Not yet, and this is a point to settle rather than let drift. The two trees
are **disjoint** (7 region identifiers in common out of 163 and 1,196, by
coincidence of function name) and measure **exactly the same metrics**: the
columns of `pairs.csv` and of `pairs.csv` are identical, except that `band`
is replaced by `stratum`/`strata`. The corpus study can therefore take over
the claims of the first draw, and on a much better population:

| | `examples/` (401) | `examples/` (403) |
|---|---:|---:|
| regions | 163 | **1,196** |
| measured pairs | 141 | 117 |
| repositories represented | 16 | **65** |
| share of the heaviest repository | **31%** (`MKLab-ITI/prophet`) | 6% |
| three heaviest repositories | **73%** | 15% |
| approved | 151 reviewed | **0** |

401's imbalance is not cosmetic: its top three repositories supply 103 of
the 141 pairs, and the first — 44 pairs, 31% — is **vendored rdflib** that
has no longer been analysed since wave 2 (§ 4, open point).

The 401 tree therefore remains **frozen, not obsolete**: it alone carries the
article's quantitative section as long as nothing is approved in 403, where
`aggregate_403` publishes `null`s by construction. It becomes removable the
day enough 403 pairs are approved to carry the same claims — **human review
is the lock**, not the tooling.

## 6. What remains to be done

1. **Settle the fate of the 44 `prophet` pairs** (§ 4) before freezing the
   article — or make the question moot by approving enough 403 pairs for the
   401 tree to leave the article (§ 5.4).
2. ~~**Raise the sampling quotas**~~ — done differently: study 403 (§ 5)
   draws 1,196 regions from 242 repositories, against 163 from 17. The point
   remains valid for the first draw, which is not replayed.
3. ~~**Cap per repository in the draw**~~ — done in 403:
   `max_per_repo_per_stratum = 4`. The **per-organisation** cap still does
   not exist, and it is the one that is missing: `prrvchr/*` and `RDFLib/*`
   each weigh several repositories.
4. **Align the 403 draw pool with the B7 criteria** (§ 5.1): it is filtered
   on the licence alone, nine repositories outside the criteria could be
   drawn. No effect to date, but latent.
5. **Split the 19 "not evaluable"** (§ 5.3) in two: package installable with
   pip versus system really absent. They are lumped together, and the
   article draws from them a property of the corpus that might be only a
   property of the venv.
6. **Split the census** rather than discard: `corpus.json` now publishes the
   full totals *and* those of the conforming stratum. Course repositories
   are a stratum, not waste.
7. Redo the **analyser audit** (`rdfeval audit`) on the enlarged corpus:
   precision (0.99) and miss rate (12%) were measured on wave 1.

## 7. Regenerating

```bash
python scripts/fetch_repo_stats.py       # full GitHub metadata (GraphQL, cached)
python scripts/export_candidates.py      # -> results/summary/candidates.csv
python scripts/selection_options.py      # the 15 criteria combinations, with counts
python -m rdfeval select                 # B7 criteria -> manifest + excluded.jsonl
python -m rdfeval acquire                # parallel clones at the pinned commit
python -m rdfeval analyze                # resumable: reuses unchanged repositories
python -m rdfeval surface                # shapes of the code, on the conforming stratum
```

`candidates.csv`: one row per distinct candidate repository (1,187), columns
`org, nom, status, motif, etoiles, commits, dernier_commit, description, url`.
Statuses: `evalue` 16, `echantillonne` 1, `controle` 1, `analyse` 389,
`elague` 37, `exclu` 743 — the `motif` field carries the list of unmet
criteria. The three numeric columns are collected on the day of the export,
not at the manifest's pinned commit.
