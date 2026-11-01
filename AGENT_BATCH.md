# Protocol of a translation batch (corpus study)

This file is the operational contract of a translator agent. The
*translation* rules are in [INSTRUCTIONS.md](INSTRUCTIONS.md) — read it
in full before starting. Here: what you edit, how you verify, and what you
return.

## Environment

- Working directory: `corpus-study/` (paths are relative to it).
- Python: `~/.venvs/ldpy/bin/python` — **always that one**, never `python3`.
- The language reference: `../ldpy/docs/reference/language/*.md`
  (transpiled and executed by the test suite: it is true).

## What you edit — and nothing else

Only the files **inside your regions' directories**:

| file | role |
|---|---|
| `translated.ldpy` | the translation (starts from a mechanical draft) |
| `driver.py` | the driver that proves equivalence |
| `fixture.ttl` | the input graph, if the region reads |
| `original.py` | **only** to make the region executable (see below) |
| `meta.json` | status, classification, constructions used, notes |
| `<shim>.py` | a context module, if bindings are missing |

**Never edit** `rdfeval/`, `config/`, `../ldpy/`, nor a region that is not
assigned to you. Run neither `git commit` nor `rdfeval strata`.

## Making the region executable — the context shim

A region extracted from a project does not run on its own: it lacks project
imports, a class, a constant. **163 regions out of 1 196 do not even have a
visible graph** (it was bound through `self.graph` or an unannotated
parameter).

The remedy is a **context module** next to the pair, imported by
`original.py`, with a header saying where it comes from.

```python
# Context shim (see meta.json): subset of projet/namespaces.py from
# owner/repo@<sha>, so the region executes outside the package.
# Identical bindings for both representations.
from rdflib import Namespace
BRICK = Namespace("https://brickschema.org/schema/Brick#")
```

Why a separate module and not lines added to `original.py`: the surface
metrics compare `original.py` with `translated.ldpy`. Any scaffolding you
invented would skew the measurement on both sides. The shim is excluded
from it (it only serves to resolve bindings).

Reproduce the context **as faithfully as possible** to the original
repository (the real IRIs, the real classes), keeping it minimal. Do not
invent logic.

## The loop, per region

1. **Read** `meta.json` (provenance, strata, oracle), `original.py`, then
   the draft `translated.ldpy`.
2. **Translate** following INSTRUCTIONS.md — the most specific
   construction, no refactoring.
3. **Write the driver.** If `meta.oracle == "values"`, the region reads:
   fill in `fixture.ttl` (several solutions, the zero-solution case,
   neighbouring data that must not match) and keep
   `fixture="fixture.ttl"`. Otherwise, the oracle is isomorphism; supply
   the call arguments if the region is a function.
4. **Verify**:
   ```
   ~/.venvs/ldpy/bin/python -m rdfeval check examples/<stratum>/<region_id>
   ```
   Transpilation, then driver. Iterate until `OK`.
5. **Fill in `meta.json`**:
   - `translation_status`: `"final"` (only if step 4 is green) or
     `"draft"` if you cannot manage it;
   - `classification`: `directly-expressible` | `minor-restructuring` |
     `awkward` | `not-expressible` | `excluded`;
   - `constructions`: the list of islands used, in the vocabulary of
     INSTRUCTIONS.md §4;
   - `translation_notes`: what required a choice, and **what is missing**
     if a construction does not cover the case;
   - `article_candidate`: `true` if the gain is visible in three lines.
   Do not touch `review.json`: the review is human.

## When it does not pass

**Do not force it.** A region that the language does not cover is a result
of the study. In order:

1. if the translation is correct but the *driver* cannot run it (external
   dependency, network, database) → `translation_status:
   "draft"`, `classification: "excluded"`, and the reason in a note;
2. if the construction exists but makes the code heavier → `awkward`, with
   the reason why;
3. if nothing covers it → `not-expressible`, with the minimal excerpt that
   shows it. This is an output of the study, not a failure.

Never set a region to `final` unless `rdfeval check` is green.

## What you return

A short report, one line per region:

```
<region_id> — <classification> — check: OK|FAIL — constructions: …
  note: <what required a choice, or what is missing>
```

Then, in three lines at most: what this batch teaches about the
construction the stratum was meant to exercise.
