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
python -m rdfeval userstudy   # draft task material -> ../user_study/config/
python -m rdfeval all         # the offline stages (analyze..userstudy)
```

Install: `pip install -e .[plots,dev]` plus `pip install -e ../semantic_python/ldpy`
(the transpiler; used for translation validation and ldpy-side metrics).
Tests: `python -m pytest tests/`.

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
