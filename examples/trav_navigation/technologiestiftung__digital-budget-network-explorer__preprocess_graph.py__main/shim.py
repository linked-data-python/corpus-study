# Context shim (see meta.json): the surrounding `main()` state that the
# region (lines 249-353 of preprocess_graph.py) reads and writes but does
# not itself define -- the input graph `g`, the `BASE` IRI prefix, the small
# string helpers (`local_name`, `first_label`, `get_top_level`,
# `extract_phrases`), the lookup tables built earlier in `main()`
# (`keywords`, `concept_labels`), and the accumulators the region appends
# into (`bereiche`, `klassen`, `hauptgruppen`, `hauptfunktionen`, `jahre`,
# `titel_beschreibung`, `posten`). Reconstructed minimally so the region
# executes standalone; no RDF logic is invented here beyond what the region
# itself performs -- these are ordinary Python helpers from the same source
# file. Identical bindings for both representations.
from pathlib import Path
from rdflib import Graph

BASE = "https://ratsvermerk.example.org/"


def local_name(uri):
    s = str(uri)
    if "#" in s:
        return s.rsplit("#", 1)[1]
    return s.rstrip("/").rsplit("/", 1)[1]


def first_label(g, uri):
    from rdflib.namespace import SKOS, RDFS
    v = g.value(uri, SKOS.prefLabel) or g.value(uri, RDFS.label)
    return str(v) if v is not None else None


def get_top_level(uri_str):
    """Walk a 'group/subgroup' path IRI up to its top-level segment."""
    prefix = BASE + "ontology#"
    if not uri_str.startswith(prefix):
        return uri_str
    local = uri_str[len(prefix):]
    top = local.split(".")[0]
    return prefix + top


def extract_phrases(text):
    return [p.strip() for p in text.split(".") if p.strip()]


def build_fixture():
    """Fresh graph plus fresh accumulators, so a run cannot leak into the
    other side's (see rdfeval.harness.fixture_graph's docstring for why the
    graph itself is parsed once per side; the accumulators are local
    dicts/lists/sets created here for the same reason)."""
    graph = Graph()
    graph.parse(str(Path(__file__).resolve().parent / "fixture.ttl"),
                format="turtle")
    keywords = {
        "energie": {"label": "Energie"},
        "schule": {"label": "Schule"},
    }
    concept_labels = {
        BASE + "ontology#soziales": "Soziales",
    }
    bereiche = {}
    klassen = {}
    hauptgruppen = {}
    hauptfunktionen = {}
    jahre = set()
    titel_beschreibung = {}
    posten = []
    return (graph, keywords, concept_labels, bereiche, klassen,
            hauptgruppen, hauptfunktionen, jahre, titel_beschreibung, posten)
