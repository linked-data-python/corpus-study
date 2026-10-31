"""Validation driver for Aleksander-Drozd__csvwlib__…__ToRDFConverter__parse_table.

The region BUILDS a graph (and, in minimal mode, takes one triple back out of
it), so the oracle is RDF isomorphism, as `meta.oracle` says.  `entry` is the
`demo` harness both files carry identically (see meta.json): the region is a
method body lifted out of its class, so `demo` rebuilds the converter, seeds
its graph with `fixture.ttl` and returns the graph the region wrote.

Three calls:

  1. minimal mode -- the `remove` site.  `_parse_row` adds
     `(dummy, csvw:describes, row_node)` for each of the two rows and the
     region removes both; what must survive is the seeded neighbourhood, which
     carries `csvw:describes` triples of its own.
  2. standard mode on the same table -- the `remove` branch is not taken and
     the three `graph.add` of the head become one `+{ … ; … }`.
  3. standard mode on a table without '@id', so `table_node` is a blank node
     rather than a URIRef -- the other side of the region's first line.

Added by the repair audit (2026-10-31):

  4. minimal mode on a table whose every column has an `aboutUrl`: `_parse_row`
     then adds nothing, and the removal must be a no-op on the neighbourhood.

  Prefix bindings.  The real constructor (ToRDFConverter.py:23-30) binds the
  RDFa initial context (`RDFGraphUtils.add_default_bindings`, csvwlib's
  `Namespaces.all()`, `csvw:` among them) and the metadata's own prefixes
  (`add_bindings_from_metadata`: `''` for a single table) before the region
  runs, and `convert()` serialises the graph when asked for a format
  (ToRDFConverter.py:43).  The context shim leaves those calls out; this
  driver puts them back, identically for both sides, by wrapping the shim's
  constructor, and compares the bindings of the returned graph on every call
  above -- the region's `@graph self.graph` with `@prefix csvw:` must not
  displace a binding the repository had already made.

  Equivalent mutants, noted and not counted: widening only the subject, only
  the object or the predicate of `-{ {dummy} csvw:describes {row_node} }`.
  `dummy` and `row_node` are blank nodes the region mints itself; in minimal
  mode the repository writes no other triple with `dummy` as subject or
  `row_node` as object (`_parse_row_data` and `parse_virtual_columns` add the
  `csvw:describes` of a row only in standard mode, ToRDFConverter.py:78-79,
  120-121), so no reachable graph holds a neighbour sharing two of the three
  terms.  Widening both ends (`?s csvw:describes ?o`) is caught by the
  fixture's own `csvw:describes` triples.
"""
from pathlib import Path

from rdflib import Namespace

import context_shim
from rdfeval import harness
from rdfeval.harness import run_pair, fixture_graph

HERE = Path(__file__).resolve().parent

TABLE_METADATA = {
    '@id': 'http://example.org/tables/people',
    'url': 'http://example.org/tables/people.csv',
    'tableSchema': {
        'columns': [{'name': 'name', 'titles': 'name'},
                    {'name': 'age', 'titles': 'age'}],
    },
}

# same table, without '@id': the region falls back to a blank node
ANONYMOUS_TABLE_METADATA = {k: v for k, v in TABLE_METADATA.items()
                            if k != '@id'}

# every column has an aboutUrl: `_parse_row` adds no csvw:describes
ABOUT_URL_TABLE_METADATA = {
    **TABLE_METADATA,
    'tableSchema': {
        'columns': [{'name': 'name', 'aboutUrl': '#person-{_row}'},
                    {'name': 'age', 'aboutUrl': '#person-{_row}'}],
    },
}

TABLE_DATA = {
    'columns': [{'name': 'name'}, {'name': 'age'}],
    'rows': [
        {'number': 1, '@id': 'http://example.org/tables/people.csv#row=2',
         'url': 'http://example.org/tables/people.csv#row=2', 'cells': {}},
        {'number': 2, '@id': 'http://example.org/tables/people.csv#row=3',
         'url': 'http://example.org/tables/people.csv#row=3', 'cells': {}},
    ],
}

# csvwlib/utils/rdf/Namespaces.py, Namespaces.all() -- transcribed verbatim
_NAMESPACES_ALL = {
    'as': Namespace('https://www.w3.org/ns/activitystreams#'),
    'csvw': Namespace('http://www.w3.org/ns/csvw#'),
    'dcat': Namespace('http://www.w3.org/ns/dcat#'),
    'dqv': Namespace('http://www.w3.org/ns/dqv#'),
    'duv': Namespace('https://www.w3.org/TR/vocab-duv#'),
    'grddl': Namespace('http://www.w3.org/2003/g/data-view#'),
    'ldp': Namespace('http://www.w3.org/ns/ldp#'),
    'ma': Namespace('http://www.w3.org/ns/ma-ont#'),
    'oa': Namespace('http://www.w3.org/ns/oa#'),
    'org': Namespace('http://www.w3.org/ns/org#'),
    'owl': Namespace('http://www.w3.org/2002/07/owl#'),
    'prov': Namespace('http://www.w3.org/ns/prov#'),
    'qb': Namespace('http://purl.org/linked-data/cube#'),
    'rdf': Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#'),
    'rdfa': Namespace('http://www.w3.org/ns/rdfa#'),
    'rdfs': Namespace('http://www.w3.org/2000/01/rdf-schema#'),
    'rif': Namespace('http://www.w3.org/2007/rif#'),
    'rr': Namespace('http://www.w3.org/ns/r2rml#'),
    'sd': Namespace('http://www.w3.org/ns/sparql-service-description#'),
    'skos': Namespace('http://www.w3.org/2004/02/skos/core#'),
    'skosxl': Namespace('http://www.w3.org/2008/05/skos-xl#'),
    'ssn': Namespace('http://www.w3.org/ns/ssn/'),
    'sosa': Namespace('http://www.w3.org/ns/sosa/'),
    'time': Namespace('http://www.w3.org/2006/time#'),
    'void': Namespace('http://rdfs.org/ns/void#'),
    'wdr': Namespace('http://www.w3.org/2007/05/powder#'),
    'wdrs': Namespace('http://www.w3.org/2007/05/powder-s#'),
    'xhv': Namespace('http://www.w3.org/1999/xhtml/vocab#'),
    'xml': Namespace('http://www.w3.org/XML/1998/namespace'),
    'xsd': Namespace('http://www.w3.org/2001/XMLSchema#'),
    'cc': Namespace('http://creativecommons.org/ns#'),
    'ctag': Namespace('http://commontag.org/ns#'),
    'dc': Namespace('http://purl.org/dc/terms/'),
    'dcterms': Namespace('http://purl.org/dc/terms/'),
    'dc11': Namespace('http://purl.org/dc/elements/1.1/'),
    'foaf': Namespace('http://xmlns.com/foaf/0.1/'),
    'gr': Namespace('http://purl.org/goodrelations/v1#'),
    'ical': Namespace('http://www.w3.org/2002/12/cal/icaltzd#'),
    'og': Namespace('http://ogp.me/ns#'),
    'rev': Namespace('http://purl.org/stuff/rev#'),
    'sioc': Namespace('http://rdfs.org/sioc/ns#'),
    'v': Namespace('http://rdf.data-vocabulary.org/#'),
    'vcard': Namespace('http://www.w3.org/2006/vcard/ns#'),
    'schema': Namespace('http://schema.org/'),
}

_shim_init = context_shim.ToRDFConverter.__init__


def _init_with_bindings(self, atdm, metadata):
    """The shim's constructor, plus the two binding calls of the real one
    (RDFGraphUtils.add_default_bindings / add_bindings_from_metadata; the
    metadata here declares no common-property propertyUrl, so the latter
    reduces to its single-table '' binding)."""
    _shim_init(self, atdm, metadata)
    for abbreviation, namespace in _NAMESPACES_ALL.items():
        self.graph.bind(abbreviation, namespace)
    if len(metadata['tables']) == 1:
        self.graph.bind('', Namespace(metadata['tables'][0]['url']) + '#')


context_shim.ToRDFConverter.__init__ = _init_with_bindings

CASES = [
    ('minimal', TABLE_METADATA),
    ('standard', TABLE_METADATA),
    ('standard', ANONYMOUS_TABLE_METADATA),
    ('minimal', ABOUT_URL_TABLE_METADATA),
]


def case(mode, table_metadata):
    """A fresh neighbourhood graph per side: the region writes into it."""
    return lambda: ((mode, table_metadata, TABLE_DATA,
                     fixture_graph(HERE / "fixture.ttl")), {})


def _bindings(graph):
    return sorted((p, str(n)) for p, n in graph.namespaces())


def _binding_diffs():
    """Bindings of the graph `demo` returns, per call, on both sides."""
    ns_o, _ = harness._exec_python(HERE / "original.py")
    ns_t, _ = harness._exec_ldpy(HERE / "translated.ldpy")
    diffs = []
    for i, (mode, meta) in enumerate(CASES):
        bo = _bindings(ns_o["demo"](mode, meta, TABLE_DATA,
                                    fixture_graph(HERE / "fixture.ttl")))
        bt = _bindings(ns_t["demo"](mode, meta, TABLE_DATA,
                                    fixture_graph(HERE / "fixture.ttl")))
        if bo != bt:
            diffs.append(f"call[{i}]: bindings differ "
                         f"(only original {sorted(set(bo) - set(bt))}, "
                         f"only translated {sorted(set(bt) - set(bo))})")
    return diffs


_BINDINGS = _binding_diffs()
_emit = harness._emit


def _emit_with_bindings(verdict):
    verdict["diffs"] = list(verdict.get("diffs") or []) + _BINDINGS
    verdict["equivalent"] = bool(verdict.get("equivalent")) and not _BINDINGS
    _emit(verdict)


harness._emit = _emit_with_bindings

VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[case(mode, meta) for mode, meta in CASES],
)
