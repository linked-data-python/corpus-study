# Protocol for an optimization batch (corpus study)

This file is the contract of an agent that writes the **two optimized
artefacts** of an already translated region (pilotage design record
`corpus/403`). The language reference is in [INSTRUCTIONS.md](INSTRUCTIONS.md)
§1: read that section, the pitfalls of §2, and §3 "What a green verdict does
not prove". The rest of INSTRUCTIONS.md concerns the faithful translation,
which is already done.

## Why

The faithful translation (`translated.ldpy`) forbids any refactoring: it
measures the notation alone, on the same program. But a reader will object
that a careful rereading of the Python would have gained as much. The two
optimized artefacts separate the two effects:

| file | what it is | what it measures |
|---|---|---|
| `optimized.py` | the **most compact** Python equivalent to `original.py`, with no island | `original.py → optimized.py`: what a careful rereading is worth |
| `optimized.ldpy` | the **most compact** LD Python equivalent to `original.py` | `optimized.py → optimized.ldpy`: what the notation is worth on top |

## The doctrine, the same on both sides (Maxime, 2026-08-29)

- **Algorithm changes allowed**: merge loops, remove intermediate
  variables, use a comprehension in place of a loop, `dict.get` in place of
  an `if … in`, etc.
- **Error handling kept**: every `try`/`except`, `raise`, and
  `if x is None: return` guard of the original survives, with the same
  effect.
- **Meaningful names kept**: no renaming to `a`, `x2`; no shortening of a
  function name, a parameter name or a public variable name.
- **No golf**: no `;` between statements, no line longer than 100
  characters that would be a folded loop, no lambda or walrus operator whose
  only purpose is to save a line. The code must remain what a demanding
  reviewer would accept in the repository.
- **Comments and docstrings**: keep those of the original, remove those that
  describe deleted code, add none.
- **The extracted header is not optimized** (decision of 2026-10-27). The
  header is everything that precedes the first line of the region, which the
  comment `# region: … (lines a-b, …)` delimits: the provenance and the
  imports of the **whole file** from which the region was drawn, plus the
  imports of the shims. It does not belong to the region: removing an unused
  import there would inflate the gain of the rereading without saying
  anything about the region. `optimized.py` takes over the header of
  `original.py` **byte for byte**, `optimized.ldpy` that of
  `translated.ldpy`. Only the lines of the region are optimized.
- **Interface unchanged**: same signature of the entry function, same
  returned value, same module-level names that the driver compares, same
  printed output. The driver (`driver.py`) is the same for the three
  artefacts; you do not touch it.

## The symmetry rule — it is what makes the measurement honest

The risk of the study: optimizing LD Python harder than Python, and thereby
rebuilding an invisible bias. Therefore:

1. **Write `optimized.py` first**, really looking for the most compact form.
   It is the point of comparison: if it is soft, all the gain attributed to
   the notation is false.
2. **Write `optimized.ldpy` from `optimized.py`**, not from
   `translated.ldpy`: replace the rdflib code with the most specific islands
   (INSTRUCTIONS.md §2, table), the rest identical.
3. **Any restructuring of `optimized.ldpy` that can also be written in pure
   Python must be carried back into `optimized.py`.** Go back and redo it.
   The only exception: a restructuring that **only an island** allows (two
   selector loops merged into one multi-pattern `m{ }`, for example). It
   stays in `optimized.ldpy` only, and you write it in
   `optimization_notes`.
4. Check by reading the two files side by side: outside the RDF lines, they
   must be identical line for line, except for the exceptions of point 3.

## What you edit — and nothing else

In the directories of **your** regions only:

| file | role |
|---|---|
| `optimized.py` | to create |
| `optimized.ldpy` | to create |
| `meta.json` | the three keys below, nothing else |

**Do not touch** `original.py`, `translated.ldpy`, `driver.py`, the
fixtures, the shims, `review.json`, nor `rdfeval/`, `config/`, `../ldpy/`.
Run neither `git commit` nor `rdfeval validate`/`compare`.

If the original carries a harness common to both versions (a `demo`
function added at the end of the file, see `meta.json`), copy it **as is**
into both optimized artefacts: it is part of the driver, not of the region,
and you do not optimize it. The shims are imported the same way as in
`original.py`.

## The loop, per region

1. Read `meta.json` (translation notes: they tell you the pitfalls already
   met), `original.py`, `translated.ldpy`, `driver.py`.
2. Write `optimized.py`, then `optimized.ldpy` (symmetry rule).
3. Check:
   ```
   ~/.venvs/ldpy/bin/python -m rdfeval check examples/<stratum>/<region_id>
   ```
   Three `OK` lines expected — `[translated.ldpy]`, `[optimized.py]`,
   `[optimized.ldpy]` — each proved against `original.py` by the same
   driver, then a `tokens: care … notation … total …` line.
4. Fill in `meta.json`:
   - `optimization_status`: `"final"` only if the three lines are `OK`,
     otherwise `"draft"`;
   - `optimization_notes`: a list of sentences — what was compressed on each
     side, each exception to the symmetry rule with its reason, and what
     could not be compressed;
   - `optimized_constructions`: the islands of `optimized.ldpy`, in the
     vocabulary of INSTRUCTIONS.md §4.

## When it does not pass

- **Nothing to compress** (the region is already minimal): that is a
  result. The two artefacts may be identical to `original.py` and
  `translated.ldpy`; say so in the notes, status `final`.
- **The driver cannot prove the artefact** without being modified (it calls
  an intermediate function that the compression removes): keep that
  function, or failing that status `"draft"` and the reason in a note. Never
  modify the driver.
- **A `FAIL`**: fix the artefact, never the driver nor the fixture.

## What you return

One line per region:

```
<region_id> — opt: final|draft — check: OK|FAIL ×3 — tokens: care … notation … total …
  note: <la compression principale, et toute exception à la symétrie>
```

Then, in two lines at most, what this batch teaches about the share of the
rereading and the share of the notation.
