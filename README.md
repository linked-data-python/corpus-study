# Empirical evaluation: RDFLib Python corpus vs Linked-Data Python

Systematic evaluation of `linked-data-python` (ldpy) against real-world
Python code that manipulates RDF through RDFLib. The pipeline supports the
claim that LD Python reduces the syntactic gap between Python and
RDF/Turtle while preserving program semantics — on *found* code, not on
hand-picked examples.

## Methodology in one paragraph

Public repositories that use RDFLib are discovered through four independent
channels (GitHub code search, GitHub repository search, Wheelodex reverse
dependencies of the `rdflib` PyPI distribution, and a curated seed list for
domain diversity), pinned to exact commits in a version-controlled manifest,
and cloned. Every Python file is analysed with an AST-based analyser that
distinguishes actual RDF operations from incidental occurrences; files are
stratified into RDF-density bands and sampled with a fixed seed. Inside
sampled files, RDF-heavy functions are extracted as regions (whole files
when function extraction would be misleading). Each region receives an LD
Python counterpart — mechanically drafted, manually reviewed, and
classified — whose semantic equivalence is established by executing both
versions and comparing the resulting RDF graphs by isomorphism (never raw
serialisation). Only equivalent pairs enter the quantitative comparison:
surface size (LOC/tokens/chars/syntax nodes), RDF-specific complexity, and
RDF/code-correspondence metrics (scaffolding tokens per triple, nesting per
term, constructors per triple). All thresholds live in
`config/evaluation.toml`; every result is stamped with the pipeline
revision and configuration version.

## Pipeline stages

```
python -m rdfeval discover    # query GitHub/Wheelodex -> manifest/discovery.jsonl
python -m rdfeval select      # inclusion criteria + commit pinning -> manifest/repositories.jsonl
python -m rdfeval acquire     # clone at pinned commits -> corpus/repos/ (gitignored)
python -m rdfeval analyze     # AST analysis -> results/raw/analysis/, files_index.jsonl
python -m rdfeval sample      # stratified seeded sampling -> results/raw/sample.json
python -m rdfeval regions     # region extraction -> results/raw/regions.jsonl
python -m rdfeval translate   # scaffold examples/<band>/<id>/ (draft translations)
#   -- human review: finalise translated.ldpy, driver.py, meta.json --
python -m rdfeval validate    # drivers -> results/raw/validation.jsonl
python -m rdfeval compare     # pair metrics -> results/raw/pairs.jsonl, summary/pairs.csv
python -m rdfeval aggregate   # stats + figures -> results/summary/
python -m rdfeval audit       # analyser precision/recall audit (hand-judged)
python -m rdfeval userstudy   # draft task material -> ../user_study/config/
python -m rdfeval all         # the offline stages (analyze..userstudy)
```

Install: `pip install -e .[plots,dev]` plus `pip install -e ../semantic_python/ldpy`
(the transpiler; used for translation validation and ldpy-side metrics).
Tests: `python -m pytest tests/`.

## Results as of 2026-08-28

60 repositories pinned, 5 812 Python files analysed, 1 557 RDF-relevant,
47 323 RDF operations. 52 sampled files → 163 regions → 40 reviewed
translations → **37 pairs proved semantically equivalent** (0 failures).

The pooled median token reduction is 0.3 %, and that number is meaningless
on its own: it pools four situations distinguished by **where the RDF of the
original actually lives**. That split is the study's main result.

| where the RDF lives | n | byte-identical | LOC | tokens | AST nodes |
|---|---:|---:|---:|---:|---:|
| inline construction (`g.add((s,p,o))`) | 10 | 1 | −3.5 % | **+13.9 %** | **+23.1 %** |
| terms only (terms mentioned, no triple asserted) | 13 | 1 | 0.0 % | +0.6 % | +0.7 % |
| string-embedded (Turtle inside a Python string) | 6 | 0 | +7.6 % | −9.1 % | −1.2 % |
| no RDF in source (external mapping/query, plumbing) | 8 | **8** | 0.0 % | 0.0 % | 0.0 % |

(positive = LD Python smaller)

- Where triples are written in the program text, the notation removes about
  a quarter of the syntax nodes.
- Where no RDF structure appears in the source, all eight translations are
  byte-identical: the notation is an exact no-op, costing nothing.
- The string-embedded rows are a **measurement artefact, not a regression**:
  Python's tokenizer counts a whole embedded Turtle document as one token,
  while the same document as an island is tokenised for real. What changes
  is kind, not size — opaque text becomes checked syntax.

RDF/code correspondence, on the same validated pairs (paired, two-sided
Wilcoxon; p-values are descriptive, effect sizes carry the argument):

| metric | RDFLib | LD Python | n | p | Cliff's δ |
|---|---:|---:|---:|---:|---:|
| scaffolding tokens per triple | 9.0 | 1.0 | 7 | 0.02 | 1.00 |
| syntactic nesting per term | 3.0 | 0.0 | 9 | 0.003 | 1.00 |
| RDFLib constructors per triple | 2.0 | 0.03 | 10 | 0.006 | 0.88 |

Analyser validity (measured, not assumed — `rdfeval audit`): precision
**0.99** on 120 hand-judged operations; **12 %** file-level miss rate on 25
hand-judged files that import rdflib with no detected operation. Densities
are therefore lower bounds — a bias against the study's own hypothesis.

## Key definitions

- **RDF operation** — a detected use of the RDFLib API: term constructors
  (`URIRef`, `Literal`, `BNode`, `Variable`), namespace constructors and
  namespace-derived terms (`FOAF.name`, `EX["x"]`), graph constructors,
  triple/quad additions (explicit 3/4-tuples), graph reads/writes,
  parse/serialize, SPARQL calls. Detection is binding-aware (imports,
  aliases, `NS = Namespace(...)`, `g = Graph()`, incl. `self.g`) — an
  imported name that is never used counts zero. See `rdfeval/analyze.py`.
- **RDF node density** — positioned AST nodes belonging to at least one RDF
  operation's subtree (each node counted once) / total positioned AST
  nodes. Bands (configurable): low < 0.05 ≤ medium < 0.20 ≤ high.
- **ldpy surface metrics** — islands are located exactly via the
  transpiler's LanguageMap; tokens = Python tokens outside islands +
  Turtle-level tokens inside (+ tokens of interpolated expressions);
  syntax nodes = masked-AST nodes + one node per term/triple/structure.
  See `rdfeval/ldpy_metrics.py` docstring for the full definitions.
- **Semantic equivalence** — same graphs (RDF isomorphism via
  `rdflib.compare`), same observable values/stdout, per example driver.
  Function regions are validated on explicit fixtures.
- **Translation classes** — `directly-expressible`, `minor-restructuring`,
  `awkward`, `not-expressible`, `excluded` (reason recorded in meta.json).

## Assumptions and limitations

- The analyser is flow-insensitive; receivers it cannot resolve are counted
  only when the argument shape is RDF-specific (recorded `certain: false`).
  Its precision and miss rate are measured by `rdfeval audit` (above), whose
  sample is hash-stable so manual verdicts survive re-analysis.
- Repositories that commit a virtualenv would otherwise contribute their
  vendored libraries (rdflib itself included) as "real-world usage";
  `site-packages`/`dist-packages`/`env*` are excluded. The sample was drawn
  before this exclusion was added, from an index that still contained
  2 549 such files — none of which was selected (verified).
- 332 files (5.7 %) are Python 2 and are recorded as unparsable rather than
  silently dropped.
- Translation and review were performed by the language's own authors. Every
  pair ships with its provenance, classification, reasoning and an executable
  equivalence check so the judgement calls can be re-examined.
- Only repositories whose licence permits snippet redistribution enter the
  example set (`snippet_licences` in config); all repositories count in the
  corpus statistics.
- The corpus is a purposive+stratified sample of public RDFLib code, not a
  probability sample of "all RDF code"; per-repository caps limit single-
  project dominance. The control sample supports a manual false-positive
  audit of the analyser.
- Collection (`( … )`) expansion triples are counted in `triples_semantic`
  but not in `triples_expressed`; both are reported.

## Reproducing

Every generated artefact carries `provenance` (UTC timestamp, git revision
of this pipeline, config/metrics versions). Re-running `sample` with the
same corpus, config and seed reproduces the sample; `manifest/` pins the
corpus itself. Raw data live under `results/raw/`, derived summaries under
`results/summary/`.
