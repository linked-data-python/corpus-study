# Protocol for a pre-review triage batch (corpus study)

This file is the contract of a **triager** agent. You translate nothing and
fix nothing: you read pairs already proved by the machine, and you tell
Maxime **which ones he must look at first, and what to look at in them**. He
cannot reread 300 pairs; he will reread those you put at the top, and
approve the others by sampling.

A useful triage is **severe and precise**: a pair put at `high` without a
verifiable reason makes him lose time, a doubtful pair left at `low` enters
the figures of the article. The translator's notes (`translation_notes`,
`optimization_notes`) are **claims to verify**, not proofs: it is often the
same kind of agent as you who wrote them.

Python: `~/.venvs/ldpy/bin/python`. The language:
[INSTRUCTIONS.md](INSTRUCTIONS.md) §1 (reference), §2 (expected
constructions and pitfalls), §3 (oracles, and "What a green verdict does not
prove"). The optimized artefacts and their doctrine:
[AGENT_OPTIMIZE.md](AGENT_OPTIMIZE.md), if the region has any.

## What you read, per region

`meta.json`, `original.py`, `translated.ldpy`, `driver.py`, the fixtures
(`*.ttl`), the shims (any other `.py`), and, if they exist, `optimized.py`
and `optimized.ldpy`. Run `~/.venvs/ldpy/bin/python -m rdfeval check "<dir>"`
once: everything must be `OK`; otherwise it is `high` by default.

## What you look for — the closed vocabulary of flags

| flag | when to raise it |
|---|---|
| `equivalence-doubt` | a case that the driver does not exercise where the two versions would behave differently (branch, `None` value, empty graph, typed literal, order, cardinality of a join, BNode…) — **say which** |
| `weak-oracle` | the driver proves little: a single call for a region with branches, a fixture that contains neither the zero-solution case nor any neighbourhood that must not match, module state that does not depend on the region, unobserved effects |
| `shim-invents-logic` | a shim or a modification of `original.py` does more than restore bindings: it adds a behaviour that is not in the original repository, or removes code from the region |
| `wrong-construction` | the translation does not use the most specific construction (INSTRUCTIONS.md §2), or `constructions` declares an island that the code does not use (undue credit) |
| `classification-doubt` | the classification (`directly-expressible`, `minor-restructuring`, `awkward`) does not match what the pair shows |
| `optimization-asymmetry` | `optimized.ldpy` is compressed harder than `optimized.py`: a restructuring written in LD Python that could also be written in pure Python, and that is not in `optimized.py` |
| `optimization-doctrine` | an optimized artefact breaks the doctrine: error handling removed, names shortened, golf, interface changed |
| `article-example` | **positive** flag: the gain reads in three lines and the pair is clean — candidate for the article |

### The defects already found — look for them first

The pilot run of 2026-10-27 found, on 14 pairs all `final` and green:

1. **The real type of the input.** An `{expr}` interpolation coerces a `str`
   into a literal where the original made an IRI of it (`<{0}>`.format):
   look at what the **original repository** really passes (the clone is
   under `corpus/repos/<owner>__<repo>/`), not at what the notes say.
2. **The truthiness of a literal.** `not g.value(…)` treats `""` and `0` as
   absent; `not bool(m{ … })` and `.first() is None` do not. Any rewritten
   truth guard is suspect.
3. **The zero-solution case and the secondary branches** absent from the
   driver: a mutant (island replaced by `[]`, predicate swapped in a
   branch) that stays green proves that the oracle is weak.
4. **A name that disappears on one side** is not compared in "module-state"
   mode (only common names are).
5. **Exceptions**: the harness compares two raises (same type, same
   message), but only on the calls the driver makes: a rewrite that moves a
   computation that can raise goes unnoticed if no call reaches the raise.
6. **The translator's notes** asserted false facts about the repository
   ("real call sites", "verbatim", "the mirror has no source"): a shim said
   to be verbatim that is not, a hand-written `__namespaces__` that the
   repository does not have (`from … import p:` unduly credited).
7. **A refactoring hidden in the faithful translation**: dispatch table,
   conditions folded into dictionaries, hoisted assignments — doable in pure
   Python, hence a gain that the measurement wrongly attributes to the
   notation. This is `classification-doubt` (the pair is not
   `directly-expressible`), and say so in the question.
8. **Needless wrappers**: `{URIRef(x)}` or `{Literal(x)}` where `f<…>` or
   `{x}` would do (`wrong-construction`, verify the equivalence).
9. **Two language deviations are known and have been escalated to Maxime**:
   `{expr}` evaluating to `None` gives `Literal("None")` (rdflib raises in
   an add, acts as a wildcard in a pattern); the object that `s{ }` yields
   does not go through `graph.query()`. Do not report them on a pair unless
   the **original repository** reaches the case (a real caller that passes
   `None`, a prepared query passed to `graph.query`), with the file and
   line in the repository.
10. **`+{ }` and `-{ }` evaluate, then write** (design record ldpy/014): if a
   term raises, the graph stays as it was, whereas a sequence of `g.add`
   leaves the triples already added. This is the intended semantics of the
   language, not a defect of the pair. Raise `equivalence-doubt` only if the
   repository **reaches** the raise (a real caller, file and line) **and can
   observe** the partial graph (it is not discarded along with the
   exception). The faithful translation then keeps the first triples in a
   separate island; the classification does not change.
11. **Prefix bindings**: `@graph g` adds the prefixes of the block to the
   graph (design record ldpy/027), so the translation may serialize
   `so:Dataset` where the original writes `<http://schema.org/Dataset>`.
   This is **not** a difference in meaning: the equivalence covers the
   triples, plus the bindings that the original sets, which must be kept;
   extra bindings are tolerated. Report it only if the repository compares
   the serialized **text** (an expected file, an exact string), with the
   file and line.

Two defects are now **checked mechanically** by the digest, do not look for
them by hand: the gap between the declared `constructions` and the islands
of the code, and a `__namespaces__` that a shim writes while the original
repository exports none (the 21 `from … import p:` credits of the corpus are
in this case).

**A mutant that mutates nothing proves nothing**: in rdflib 7.2.1,
`FILTER(false)` filters nothing (`FILTER(1 = 2)` does). To kill a branch,
write `FILTER(1 = 2)` or a nonexistent predicate, and check that the mutant
does change the result on a simple case.

Verify instead of assuming. You may **experiment in a copy**:
`work=$(mktemp -d)` then `cp -r "<dir>" "$work/"` — always a folder created
by `mktemp -d`, never a fixed name: other triagers work at the same time in
the same temporary directory. Corrupt a line of the translation or add a
call to the driver in the copy, and run `rdfeval check` on the copy
(command with the path of the copy). A doubt confirmed by an experiment is
worth more than ten plausible doubts; say in the question what the
experiment showed. Delete your copies at the end.

## The priority

- **`high`**: an `equivalence-doubt`, `weak-oracle`, `shim-invents-logic` or
  `optimization-asymmetry` flag that you have verified or that you can show
  by a precise line; or a failing `check`. These are the pairs that can skew
  a figure.
  For `weak-oracle`, `high` requires that a mutant that **removes an island
  or widens a bound term** stays green. If only cardinality mutants survive
  (`.first()` → `.one()`, `[:1]`) and you have established the equivalence
  by hand-made cases, it is `medium`.
- **`medium`**: `wrong-construction`, `classification-doubt`,
  `optimization-doctrine`, or a `high` flag that remained plausible without
  proof.
- **`low`**: none of the above. A `low` pair may carry `article-example`.

## What you write — `triage.json`, and nothing else

In the directory of each region, a single file, `triage.json`:

```json
{
  "priority": "high",
  "flags": ["equivalence-doubt"],
  "summary": "One sentence: what is wrong, or \"nothing to report\".",
  "questions": [
    {
      "question": "A CLOSED question for Maxime, answered by yes or no.",
      "where": "translated.ldpy:14 and original.py:12",
      "if_yes": "what it implies for the pair (e.g. approve)",
      "if_no": "what it implies (e.g. needs-work, add a driver call with an empty graph)"
    }
  ],
  "evidence": "What you ran to check it, and the result. Empty if nothing.",
  "triaged_by": "sonnet-5.5"
}
```

At most one question per flag, none for `low` except `article-example`
("Can this pair illustrate the article?"). `where` cites real files and
line numbers.

**Edit nothing else**: neither the pair, nor `meta.json`, nor `review.json`,
nor `rdfeval/`. Do not commit.

## What you return

One line per region:

```
<region_id> — <priority> — <flags> — <summary>
```

Then, in two lines at most, a defect that recurs from one region to another
in this batch, if there is one.
