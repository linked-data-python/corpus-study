# Translator instructions — the corpus study

You translate regions of real rdflib code, drawn from a sample stratified
by *kind of use*, into **linked-data-python** (ldpy).

**What we want to find out** — for each construction of the language: does
it serve on real code, where, how many times, and with what gain? A region
that nothing covers is a **result**, not a failure. Never work around it:
report it.

Reference design records: [`corpus/403`](../corpus/403-evaluation-absorption-complete.md)
(the protocol), [`404`](../corpus/404-outillage-tirage-stratifie.md)
(the draw), [`405`](../corpus/405-oracle-de-lecture.md) (the reading
oracle). You do not have to read them to translate: everything you need is
below.

---

## 1. The whole language, right here

This section replaces the reading of the nine pages of
`../ldpy/docs/reference/` (~8 500 words) that these instructions used to
require. It is **generated**, not copied: it cannot drift from the real
language.

<!-- BEGIN island-reference (generated: sync_language_reference.py) -->

**Declarations**

| form | what it is |
|---|---|
| `@prefix ex: <IRI> [as EX] .` | Binds `ex:` to a namespace IRI for the rest of the enclosing block. A prefix is lexical: `ex:` on its own is never a value. When the code needs the Namespace as an OBJECT — to `bind()` it on a graph, to export it, to put it in a registry — `as EX` binds that object to a Python name too. Declaring the prefix again in a deeper block shadows it, the way a Python name would. |
| `@base <IRI> .` | Sets the base against which relative IRIs are resolved for the rest of the block, so that `<sensor/1>` means `<IRI>sensor/1`. |
| `from MODULE import ex:, unit: as u:` | Imports prefixes declared by another module, optionally renaming them. The module is imported as usual; what travels is the prefix bindings, which have no value to import by ordinary means. |
| `@graph EXPR \| @graph as NAME -> Graph` | Designates the current graph for the block — the one `+{ }`, `-{ }` and a receiver-less `m{ }` act on. `as NAME` creates a fresh graph and binds it to NAME; `global` and `nonlocal` widen the scope. Either way the graph inherits the block's prefixes, so it serialises with them. |
| `@bindings EXPR \| @bindings as NAME -> Bindings` | Designates the current bindings: the mapping that gives `?name` its value in the enclosing block. Any mapping will do, and `as NAME` creates an empty one. |
| `for @bindings [as NAME] in ITER:` | Loops over an iterable of mappings, making each row the current bindings for the body. A `csv.DictReader` and the solutions of `m{ }` are both iterables of mappings, so both drive this loop. |

**Terms**

| form | what it is |
|---|---|
| `<IRI> -> URIRef` | An absolute IRI, or a relative one resolved against the `@base` in scope. |
| `ex:local -> URIRef` | A prefixed name: the local part is appended to the IRI bound to `ex:`. Turtle's character set applies inside an island, so `o-pizza:topping` and `ex:café` are names here although neither is a legal Python expression. `ex:{expr}` computes the local part. |
| `"..."@lang \| "..."^^dt -> Literal` | An RDF literal carrying a language tag or a datatype. The quoted part may be an f-string, and `{expr}` may supply the datatype itself. |
| `?name \| $name -> Variable` | A SPARQL variable. In a pattern it is what gets matched and projected; in `g{ }` or `+{ }` it takes its value from the current bindings, and leaves the triple out when it has none. |
| `f<...{expr}...> -> URIRef` | A formatted IRI: the braces interpolate as in an f-string, and the result is resolved against `@base` if it is relative. It does NOT percent-encode — the shape of the IRI is yours. To mint one from data that may hold a space or a slash, use `e<...>`, which encodes. |
| `f{expr} \| ?{expr} -> Node` | Coerces any Python value into an RDF term, by the coercion policy in scope. Two spellings of one operation: `?{ }` reads better in term position, `f{ }` beside `f<...>`. |
| `_:{expr} -> BNode` | A blank node whose identity is its data: the same value gives the same node anywhere in the program, so two rows that share a key join without inventing an IRI for them. |

**Graphs and the current graph**

| form | what it is |
|---|---|
| `g{ ... } -> Graph` | Builds an RDF graph from Turtle written in place. `{expr}` interpolates a Python value in term position, and each occurrence is evaluated once. The braces are an expression, so a `g{ }` goes anywhere a value goes — a default argument, a comprehension, a return. |
| `+{ ... } [ (GRAPH) ]` | Adds the triples to the current graph. `?name` takes its value from the current bindings, and a triple with an unbound variable is dropped rather than written half-way. A trailing `(g)` names another receiver. |
| `-{ ... } [ (GRAPH) ]` | Removes from the current graph every triple matching the pattern. An unbound variable is a wildcard here, not a hole: this is a SPARQL `DELETE WHERE`, not a list of triples to subtract. |

**Reading**

| form | what it is |
|---|---|
| `m{ ... } -> Solutions` | Matches a basic graph pattern against the current graph, lazily. Iterating yields a bare term when one variable is projected and a tuple otherwise; `.one()`, `.first()`, `.count()` and `bool()` are the usual reductions. A `(graph)` suffix names another source. |
| `s{ ... } -> Query` | A SPARQL query or update, parsed when the file is transpiled rather than at run time. `{expr}` in term position becomes an initial binding — never string pasting, so nothing here can be injected. Calling it on a graph gives a LAZY query; `.execute()` is what forces it — for an update, and for any query whose rdflib `Result` you then call a method on. |

**Deferred evaluation**

| form | what it is |
|---|---|
| `e{ ... } -> Expr` | A deferred SPARQL expression. It is not evaluated where it is written, but against the bindings in force when the island holding it is instantiated — once per row of a `for @bindings` loop. `{python}` holes are evaluated where they are written. |
| `e<...{?var}...> -> Expr` | A deferred IRI: `f<...>`'s interpolation, except that the holes are SPARQL expressions re-evaluated for each set of bindings — and that it percent-encodes what it interpolates. This is the form for minting an IRI from a data column. |

*(Generated from `ldpy/lsp/islanddoc.py` — the table the editor's hover shows. `ldpy/tests/test_islanddoc.py` guarantees that it describes **every** kind of island and that each of its links lands on a live anchor of the documentation. Do not edit it by hand: `python scripts/sync_language_reference.py`.)*

<!-- END island-reference -->

Three things the table does not say, and which decide most translations:

- **the adjacency rule.** An island opens only if the sigil touches the
  brace: `e{` opens one, `e {` does not; `euler + 1` remains Python.
  Likewise `{ex:b2}` is a set containing an IRI, whereas `{ex : b2}` is a
  dictionary. When in doubt, write the form in a file and transpile it.
- **an island is an expression.** `g{ … }` goes anywhere a value goes:
  default argument, comprehension, `return`, lambda. `+{ }` and `-{ }` are
  *statements*, including as the suite of a one-line `if`.
- **the transpiler is the arbiter.** `python -m ldpy fichier.ldpy` settles
  any question of form, and settles it faster than the documentation. What
  you believe you know by analogy with Turtle or SPARQL is not reliable.

To go further on a specific point — and only then — the documentation is at
`../ldpy/docs/`: `reference/language/lexical.md` for the three
disambiguation rules and the known limits, `how-to/migrate-from-rdflib.md`
for the table of mechanical rewrites with their pitfalls. All the
documentation is transpiled, executed, and its assertions checked by the
test suite: what it shows is true today.

---

## 2. Always the most specific construction — never degrade

The aim of the study is to credit or debit **each island separately**. A
translation that writes everything as `s{ SELECT … }` measures nothing.

Mapping from rdflib idiom to expected construction, by stratum of the draw:

| stratum | rdflib idiom | expected construction |
|---|---|---|
| `ns_import_project` | `from projet.ns import BRICK, SH` | `from projet.ns import brick:, sh:` |
| `ns_def_local` | `NS = Namespace("…")` in a function | `@prefix ns: <…> .` in the block |
| `add_isolated` | an isolated `g.add((s, p, o))` | `@graph g` + `+{ … }` |
| `add_run_shared_subject` | several `.add` calls on the same subject | **a single** `+{ s p1 o1 ; p2 o2 }` |
| `add_in_loop` | `.add` in a loop over rows | `for @bindings in …:` + `+{ }` with `?var` |
| `remove` | `g.remove((s, p, None))` | `-{ s p ?o }` (unbound variable = wildcard) |
| `trav_one_step` | `for o in g.objects(s, p)` | `for o in m{ {s} p ?o }` |
| `trav_navigation` | nested loops of selectors | **a single** multi-pattern `m{ }` (join) |
| `trav_single_value` | `g.value(s, p)`, `next(g.subjects(…))` | `m{ … }.first()` / `.one()` |
| `trav_existence` | `(s, p, o) in g`, `any(g.objects(…))` | `bool(m{ … })` |
| `sparql_literal` | `g.query("SELECT …")` | `s{ SELECT … }` |
| `sparql_interpolated` | query assembled by f-string/`+` | `s{ … {expr} … }`, interpolation in term position |
| `bind_initbindings` | `initBindings=`, `initNs=` | interpolated term in `s{ }` **if the variable is not projected**; otherwise `s{ … }(bindings=…)`; prologue inherited from the `@prefix` declarations |
| `coercion_datatype` | `Literal(x, datatype=…)` on a computed value | the language's coercion, or `"…"^^xsd:…` if the value is constant |

Explicit prohibitions:

- **no `s{ }` where `m{ }` will do.** A `g.value` becomes `m{ }.first()`,
  never a SELECT query.
- **no `.add()` kept** when `+{ }` covers the case.
- **no assembled query string**: the interpolation of `s{ }` is in term
  position and becomes an `initBindings`, never a textual substitution.
- **no refactoring.** The comparison must be *same program, same RDF
  behaviour, different notation* — not *old implementation against
  redesigned implementation*. Do not reorder, do not merge functions, do
  not "clean up" anything.

Known pitfalls, not to be reproduced:

- **A pattern received as DATA is out of reach, and the failure is
  silent.** `-{ }` and `m{ }` take a WRITTEN pattern; the wildcard there is
  lexical (an unbound variable), not a value. An `(s, p, o)` with `None`s
  received as an argument — `Store` API, `delete(pattern)` helper —
  interpolated as `-{ {s} {p} {o} }` gives `Literal('None')` and removes
  **nothing, without any error**. Keep `.remove()` and report it.
- **A multi-pattern `-{ }` JOINS.** Independent `remove` calls on the same
  subject cannot be factored with `;`: `-{ ?s a ex:C ; ex:p ?o }` is a
  `DELETE WHERE`, and it deletes nothing if one of the patterns is missing.
  One `remove` per island.
- **Folding a "single value" read into a join changes the cardinality.** A
  multi-pattern `m{ }` is a product: if the added pattern can match several
  times where the original consumed only the first value (`g.value`,
  `next`), the join produces more solutions than the original loop. Fold
  only if the code already treats "the first or none" as its semantics.
- **`ex:{?v}` concatenates without encoding** (it is instantiated as of
  0.4.0, see §2 bis). To mint an IRI from a column that may contain a space
  or a slash, `e<http://…/{?id}>` is the form that encodes.
- **`_:label` is not `BNode("label")`.** If the *label* reaches a
  serialisation or a hash (signature, artefact code), keep `{BNode(...)}`.
- **`Literal(n, datatype=…)` is not `"n"^^dt`** when `n` is not a string:
  read `how-to/migrate-from-rdflib.md`, pitfall 1.
- **`URIRef(x)` is not `f<{x}>`** if a `@base` is in scope: pitfall 2 of the
  same page.

---

## 2 bis. What the language gained in 0.4.0

Four changes, all implemented and tested. They make some habits acquired
before this version obsolete.

- **`ex:{?id}` is instantiated.** The local part of a prefixed name was the
  only term position where a variable was not instantiated: it produced
  `ex:id`, the same IRI on every row, without any error. It now resolves
  against the current bindings. Beware: `ex:{…}` **concatenates without
  encoding**; it is `e<…{?id}>` that percent-encodes. Choose according to
  whether the value may contain a space or a slash, and say so in a note.
  On an ordinary value, `ex:{expr}` remains immediate and requires no
  bindings.
- **`+{ }` and `-{ }` as the suite of a compound statement.**
  `if cond: +{ … }` on a single line is accepted. There is thus no need to
  open a block for a one-line `if` — which is precisely what made
  translations longer.
- **`b.raw`.** On `for @bindings as b in rows:`, `b[key]` is the RDF term
  and `b.raw[key]` the value as it arrived. This is what you need when the
  original tests `if row[col] != "":`, because `Literal("") != ""`.
- **"Declared prefix = Python name" warning**: the transpiler now reports
  it. If it appears, it is a real pitfall of the file, not noise.

Two fidelity pitfalls, verified on rdflib 7.2.1, that have already produced
wrong translations:

- `Literal('x')` and `Literal('x', datatype=xsd:string)` **are not equal**:
  the first has a null `datatype`. Translating `Literal(v, XSD.string)` as
  a bare interpolation `{v}` therefore changes the graph. You need
  `{v}^^xsd:string`.
- `Literal(True, datatype=XSD.boolean)` is `"true"` whereas `f"{True}"` is
  `"True"`: rdflib normalises the lexical form of a typed literal built
  from a Python value. The mechanical rewrite is safe only if the value is
  already a string.

A call that no longer exists in 7.2.1: **`Graph.load` has been removed**
(a deprecated alias of `Graph.parse`). A region that calls it runs on
neither side; replace it with `.parse(...)` on both sides, identically,
and say so in `translation_notes` — the change affects no RDF meaning.

And a scoping subtlety, to know before designating a graph: **`@graph g`
captures the VALUE of `g` at its line, not the name.** If the code
reassigns `g` later (`g = g + autre`), a new `@graph g` declaration is
needed after the reassignment, otherwise writes go to the graph that has
become unreachable — silently.

---

## 3. Exact semantics, proved — two oracles

Every pair must be **proved equivalent by execution**, not judged by eye.
The driver (`driver.py`) runs both versions and prints its verdict.

### Region that BUILDS a graph → RDF isomorphism

```python
from rdfeval.harness import run_pair
VERDICT = run_pair(__file__)                     # compares the module's graphs
```

### Region that READS a graph → equality of the values produced

Write an **input graph** `fixture.ttl` next to the pair; it is parsed into
a fresh graph for each version.

```python
from rdfeval.harness import run_pair
VERDICT = run_pair(__file__, entry="ma_fonction", fixture="fixture.ttl")
```

The fixture is a translation act in its own right. It must cover:

1. the pattern the region reads, with **several** solutions;
2. the **zero-solution** case (where `g.value` returns `None`, `.first()`
   must return `None` too);
3. **neighbouring data that must not match** — otherwise a pattern that is
   too broad goes unnoticed.

Results are compared as **multisets**: no store guarantees an order. If the
region imposes an order (`sorted(...)`, `ORDER BY`), say so:
`run_pair(..., ordered=True)`.

### What a green verdict does not prove

That the two versions coincide **on this fixture**. A poor fixture makes a
green worthless. Write it against the region, not against the translation.

---

## 4. Label the constructions used

Each translated region declares, in its `meta.json`, the constructions it
uses — this is what allows each island to be credited separately:

```json
{
  "translation_status": "final",
  "classification": "directly-expressible",
  "constructions": ["@prefix", "@graph", "+{ }", "m{ }", ".first()"],
  "strata": ["trav_single_value", "add_isolated"],
  "translation_notes": ["…"]
}
```

**Construction vocabulary — closed list.** These exact strings, and no
others: they are the study's main measure, and one construction written in
two ways becomes two constructions in the table. The list lives in
`rdfeval/constructions.py` (it normalises the common variants, and flags
what it cannot place).

```
@prefix   @base   from … import p:   @graph   @bindings   for @bindings in
g{ }   +{ }   -{ }   _:{ }
m{ }   s{ }   .first()   .one()   .count()   .execute()
e{ }   e<…>   f<…>   f{ }
IRI   prefixed name   typed literal   language literal   plain literal
variable   interpolation {expr}
call suffix (g)   global/nonlocal modifier
```

A construction missing from this list is something to report, not a
licence to invent: put it in `translation_notes`.

**This is not a mere formatting rule, and the 2026-08-29 campaign showed
it.** It wrote `nom préfixé`, `nom prefixe` and `prefixed name` for one and
the same construction; `suffixe d'appel (g)` next to `call suffix (g)`;
`littéral typé`, `litteral type` and `typed literal`; `f<...>` next to
`f<…>`. Seven apparent constructions where there were three.
`constructions.normalise` collapsed them — the published counts are
correct — but it can only collapse what it has already seen. Write the
labels **in English, without accents, exactly as above**, copying them
from this list rather than retyping them from memory.

Translation classification:
`directly-expressible` · `minor-restructuring` · `awkward` ·
`not-expressible` · `excluded`.

---

## 5. Report instead of working around

If a construction does not cover the region:

1. **do not bend the region** to make it fit;
2. classify it `awkward` or `not-expressible`;
3. write in `translation_notes` **exactly what is missing**, with the
   minimal excerpt that shows it;
4. if it is a defect of the language and not an accepted limit, it is a
   finding of the kind recorded in design record `ldpy/012` — it is passed
   up as is.

Findings already known (do not rediscover them, but confirm them if you
come across them): reads with no dedicated island prior to `m{ }`, `@graph`
on a read-only property, line-number drift on multi-line islands.

---

## 6. The procedure, per batch

```
python -m rdfeval strata          # the draw (already done: results/raw/strata.json)
#   -- translation by batch: see below --
python -m rdfeval validate        # runs the drivers -> results/raw/validation.jsonl
python -m rdfeval compare         # pair metrics
python -m rdfeval aggregate       # aggregates and figures
```

A batch = a set of regions of the same stratum. For each one:

1. read the region (`source`) **and its context** (`context`) in
   `results/raw/strata.json`;
2. write `original.py` (provenance header + context + source),
   `translated.ldpy`, `driver.py`, `fixture.ttl` if the region reads,
   `meta.json`;
3. **transpile**: `python -m ldpy translated.ldpy` must pass;
4. **run the driver**: the verdict must be `equivalent: true`;
5. only then, `translation_status: "final"`.

A pair that has not passed 3 and 4 **does not enter human review**: the
machine checks are pre-conditions, not an after-the-fact filter.

163 of the 1 196 regions carry no RDF operation once extracted: the graph
is bound there through an attribute (`self.graph`) or an unannotated
parameter that the context lines cannot carry. **Restore the binding** in
`original.py` (an annotated parameter, an assignment in the context) — this
is expected, it is not a region to discard.

## 7. One publishable example per stratum

Each stratum must provide **at least one publishable before/after pair**
for the article, chosen among the approved regions, with its provenance
(repository, file, commit). If a region you translate is particularly
telling — the gain is visible in three lines — note it:
`"article_candidate": true` in `meta.json`.
