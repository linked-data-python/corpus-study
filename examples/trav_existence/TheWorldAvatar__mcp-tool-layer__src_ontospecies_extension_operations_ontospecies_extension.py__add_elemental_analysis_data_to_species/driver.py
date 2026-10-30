"""Validation driver for TheWorldAvatar__mcp-tool-layer__src_ontospecies_extension_operations_ontospecies_extension.py__add_elemental_analysis_data_to_species.

add_elemental_analysis_data_to_species opens its graph through `with
locked_graph() as g:` and returns only a plain string (str(ea), or an error
message) -- never the graph itself, which is also not one of its own
parameters. run_pair's built-in entry=/calls= comparison only ever looks at
a function's RETURN VALUE and its own positional/keyword ARGUMENTS, so it
cannot see what got written to `g`: comparing just the returned string would
be exactly the "hollow green" INSTRUCTIONS SS5 warns about, since the string
(built from a deterministic stand-in `ea`, see context_shim.py) is identical
whether or not the tail +{ }(g) call under test actually ran.

So, following the precedent set by the sibling region
add_isolated/..._add_atomic_weight_to_element/driver.py (also bypassing
run_pair's call loop for a region whose real state does not travel through a
return value or an argument), this driver drives both sides by hand: call
the "original" fully, snapshot the graph context_shim.locked_graph handed it
(context_shim.LAST_GRAPH), THEN call the "translated" version and snapshot
ITS graph, THEN compare the two snapshots by isomorphism. The two calls
never overlap -- call, snapshot, reset, call, snapshot -- so there is no
race on the shared context_shim.LAST_GRAPH slot (module imports are cached,
so both sides' `from context_shim import ...` resolve to the same module
object).

Unlike that sibling, this region READS the graph first (the "species
exists" check, the trav_existence construction this stratum exercises) --
so the graph must arrive PRE-POPULATED. `fixture.ttl` supplies it: parsed
once here, its triples are replayed into `context_shim.SEED` before every
call, so locked_graph() seeds each side's fresh Graph() identically. It
holds two os:Species (several solutions of the pattern) and a same-shaped
neighbour typed os:Element (must not satisfy the check); the zero-solution
case is exercised by querying a species IRI absent from the fixture
altogether (case 2 below).

Five cases exercise every path through the region:
  * an existing species, calculated-value branch (reaches the exists=True
    path, the calculated WeightPercentage node, and the tail add);
  * a second existing species, experimental-value AND molecular-formula
    branches (the other two conditional adds);
  * a species IRI absent from the fixture (exists=False, the bool(m{ })
    construction returning false, the catalog-error return -- proves no
    spurious triple is written on this path);
  * missing species_iri/data_label (earliest return, graph never touched);
  * a non-absolute species_iri (the _is_abs_iri guard, graph never
    touched).

Five more since the 2026-10-30 repair (see CASES): the two neighbours of
the existence check, which the fixture held but no call queried, so that
widening the class or the predicate of `m{ }` to a variable stayed green;
an empty data_label; empty optional texts; all three optional branches in
one call.
"""
from __future__ import annotations

import traceback
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import _exec_ldpy, _exec_python, _emit, graphs_isomorphic, fixture_graph

import context_shim

HERE = Path(__file__).resolve().parent

SEED_TRIPLES = list(fixture_graph(HERE / "fixture.ttl"))

CASES = [
    dict(species_iri="https://example.org/species/S1", data_label="EA1",
         calculated_value_text="12.3"),
    dict(species_iri="https://example.org/species/S2", data_label="EA2",
         experimental_value_text="9.5", empirical_molecular_formula="H2O"),
    dict(species_iri="https://example.org/species/S9", data_label="EAx"),
    dict(species_iri="", data_label="EAy"),
    dict(species_iri="not-an-absolute-iri", data_label="EAz"),
    # Added by the 2026-10-30 repair -- the existence check against its
    # neighbourhood, and the falsy arguments of the region's guards:
    #   * NotASpecies is typed os:Element: an rdf:type with another class
    #     must answer "not found" (kills the class widened to `?c`);
    #   * SeeAlso names os:Species under rdfs:seeAlso: another predicate
    #     must answer "not found" (kills rdf:type widened to `?p`);
    #   * an empty data_label (the second half of the first guard);
    #   * every optional text given as "" on an existing species: the three
    #     `if <text>:` branches are skipped, only the EA node and the tail
    #     `+{ }` are written;
    #   * all three optional branches in ONE call, as the repository's own
    #     example does (ontospecies_extension.py:694-699): the two
    #     WeightPercentage nodes are minted in the same call.
    dict(species_iri="https://example.org/species/NotASpecies", data_label="EAn"),
    dict(species_iri="https://example.org/species/SeeAlso", data_label="EAs"),
    dict(species_iri="https://example.org/species/S1", data_label=""),
    dict(species_iri="https://example.org/species/S2", data_label="EAe",
         calculated_value_text="", experimental_value_text="",
         empirical_molecular_formula=""),
    dict(species_iri="https://example.org/species/S1", data_label="IRMOP-50 EA",
         calculated_value_text="C 37.94, H 4.96, N 3.63",
         experimental_value_text="C 37.93, H 4.76, N 3.62",
         empirical_molecular_formula="C108H84N12O88S12"),
]

verdict = {"example": HERE.name, "equivalent": False,
           "method": "entry:add_elemental_analysis_data_to_species",
           "diffs": [], "error": None}

try:
    ns_o, out_o = _exec_python(HERE / "original.py")
    ns_t, out_t = _exec_ldpy(HERE / "translated.ldpy")
    fo = ns_o.get("add_elemental_analysis_data_to_species")
    ft = ns_t.get("add_elemental_analysis_data_to_species")
    if not callable(fo) or not callable(ft):
        raise RuntimeError("entry point not found in both modules")

    diffs: list[str] = []
    for i, kwargs in enumerate(CASES):
        context_shim.SEED = SEED_TRIPLES
        context_shim.LAST_GRAPH = None
        ro = fo(**kwargs)
        go = context_shim.LAST_GRAPH or Graph()

        context_shim.SEED = SEED_TRIPLES
        context_shim.LAST_GRAPH = None
        rt = ft(**kwargs)
        gt = context_shim.LAST_GRAPH or Graph()

        if ro != rt:
            diffs.append(f"case[{i}]: result differs ({ro!r} vs {rt!r})")
        if not graphs_isomorphic(go, gt):
            diffs.append(f"case[{i}]: graphs not isomorphic "
                         f"({len(go)} vs {len(gt)} triples)")

    if out_o != out_t:
        diffs.append(f"stdout differs ({out_o[:200]!r} vs {out_t[:200]!r})")

    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)

_emit(verdict)
VERDICT = verdict
