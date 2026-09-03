# Context shim (see meta.json): the names original.py imports from
# acro.ontology_handler. populate_useful_dicts is the real function
# (verbatim from the pinned commit) -- this region's own assertions
# exercise it, so a stub would not discriminate a broken translation from a
# correct one. It also records the graph it is called with in LAST_GRAPH,
# purely for the driver's demo() harness (see driver.py): the region under
# study builds `g` as a local variable and never returns or exposes it
# otherwise. The other imported names are never called by this region and
# are stubbed. From AI-SDC/ACRO@eb1d6e370a : acro/ontology_handler.py.
# Identical bindings for both representations.
import rdflib

PREFIX = "https://www.w3id.org/statbarnsdc#"
SUBCLASS = "http://www.w3.org/2000/01/rdf-schema#subClassOf"

LAST_GRAPH = None


def populate_useful_dicts(g: rdflib.Graph) -> tuple:
    global LAST_GRAPH
    LAST_GRAPH = g

    definitions: dict = {}
    pref_labels: dict = {}
    othersuperclasses: dict = {}

    for s, p, o in g:
        key = s.replace(PREFIX, "")
        oval = str(o)
        if str(p) == "http://www.w3.org/2004/02/skos/core#definition":
            definitions[key] = oval
        if str(p) == "http://www.w3.org/2004/02/skos/core#prefLabel":
            pref_labels[key] = oval
        if (
            str(p) == SUBCLASS
            and not oval.startswith("https://w3id.org")
            and not oval.startswith(PREFIX)
        ):
            if key in othersuperclasses:
                othersuperclasses[key].append(oval)
            else:
                othersuperclasses[key] = [oval]

    assert set(definitions.keys()) == set(pref_labels.keys())
    return definitions, pref_labels, othersuperclasses


def is_uri(*args, **kwargs):
    raise NotImplementedError("not used by this region")


def make_ischeckedby(*args, **kwargs):
    raise NotImplementedError("not used by this region")


def make_ismitigatedby(*args, **kwargs):
    raise NotImplementedError("not used by this region")


def make_save_analyses(*args, **kwargs):
    raise NotImplementedError("not used by this region")


def make_save_risks(*args, **kwargs):
    raise NotImplementedError("not used by this region")


def make_save_statbarns(*args, **kwargs):
    raise NotImplementedError("not used by this region")


def print_nested_dict(*args, **kwargs):
    raise NotImplementedError("not used by this region")
