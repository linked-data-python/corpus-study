# Protocol for a post-triage repair batch (corpus study)

This file is the contract of a **repairer** agent. A triager
([AGENT_TRIAGE.md](AGENT_TRIAGE.md)) read the pair and wrote `triage.json`:
a priority, flags, and closed questions addressed to Maxime. Many of these
questions do not need him: "the driver does not exercise the zero-solution
case", "a mutant stays green", "the translation fails when the input is a
`str`". They are settled by strengthening the driver, and by fixing the
translation if the strengthened driver makes it fail. That is your job;
what really remains to be judged goes back to Maxime.

Python: `~/.venvs/ldpy/bin/python`. The language and its pitfalls:
[INSTRUCTIONS.md](INSTRUCTIONS.md) §1 to §3. The translation protocol (what
a driver, a shim, a fixture is): [AGENT_BATCH.md](AGENT_BATCH.md).

## What you handle

The `weak-oracle` and `equivalence-doubt` flags of `triage.json`. The others
(`wrong-construction`, `classification-doubt`, `optimization-doctrine`,
`shim-invents-logic`, `article-example`) are judgements: you do not handle
them, except a material error in `constructions` in `meta.json` (a declared
island that is not used, or used and not declared), which you fix.

## The loop, per region

1. Read `triage.json` (questions and `evidence`), then the pair as a
   triager would.
2. **Strengthen the driver first, without touching the translation**: add
   the calls, the branches, the zero-solution case, the `""`/`0` literal,
   the input type that the repository **actually** uses (clone under
   `corpus/repos/`), the neighbourhood in the fixture that must not match,
   the comparison of what the region writes (file, attribute). The
   strengthened driver must make the mutants the triager cited fail: check
   it in a copy (`work=$(mktemp -d)`), mutant by mutant.
3. Run `rdfeval check` on the region.
   - **Green**: the doubt was unfounded, and it is now lifted by a proof.
   - **Red on `translated.ldpy`**: the translation was wrong. Fix
     `translated.ldpy` (the most specific construction that remains
     correct, INSTRUCTIONS.md §2), until green. If nothing correct exists
     in the language, `classification: "not-expressible"`, with the minimal
     excerpt, and it is a result of the study.
   - **Red on an optimized artefact**: fix it the same way.
4. The strengthened driver applies to the three artefacts: `check` must
   return all its lines `OK` at the end.

**A mutant that mutates nothing proves nothing**: in rdflib 7.2.1,
`FILTER(false)` filters nothing (`FILTER(1 = 2)` does). To kill a branch,
write `FILTER(1 = 2)` or a nonexistent predicate, and check that the mutant
does change the result on a simple case.

**Prefix bindings**: when the repository serializes or rereads the bindings
of a graph, the driver compares the triples and requires that every binding
set by the original be found in the translation; it tolerates extra
bindings (`@graph` adds those of the block, record ldpy/027) and does not
compare the serialized text, unless the repository itself compares an exact
text.

A driver remains **readable**: a docstring that says what each call
exercises, and why. Never weaken a driver, never remove any existing call.

## What you write

In the directories of **your** regions only: `driver.py`, the fixtures,
`translated.ldpy` and the optimized artefacts if necessary, and in
`meta.json`:

- `translation_notes`: add one sentence per fix of the translation (what
  was wrong, the proof);
- `repair`: an object `{"date": "YYYY-MM-DD", "driver": "what was added
  to the driver", "translation_fixed": true|false, "mutants_killed":
  ["…"], "remaining": "what is left for Maxime to judge, or empty"}`.

In `triage.json`, add only one key: `"repaired": "<one sentence>"`. Do not
change the priority nor the questions: the triage remains the triage,
Maxime will read the repair alongside it.

**Do not edit** `original.py` (except to make it executable, as in
AGENT_BATCH.md), the shims except to supply a real input type,
`review.json`, nor `rdfeval/`. Do not commit.

## What you return

```
<region_id> — driver: strengthened|unchanged — translation: fixed|correct — check: OK|FAIL — remaining: …
```

Then, in two lines at most, what these repairs teach about the drivers of
the campaign.
