# Extracted from hidden-graph/rdflib-starlight@b7973da2b5 : starlight/graph/starlight_graph.py
# region: StarlightGraph.parse (lines 1134-1237, stratum remove)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import RDF
_RDF_TRIPLE_TERM = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#TripleTerm'

elif format in ('nt12', 'nq12'):
    from starlight.parsers.ntriples12 import extract_version_directive
    if format == 'nt12':
        from starlight.parsers.ntriples12 import parse_ntriples12
        triples = parse_ntriples12(text)
    else:
        from starlight.parsers.ntriples12 import parse_nquads12
        # merge all named graphs: drop the graph component
        triples = [(s, p, o) for s, p, o, _g in parse_nquads12(text)]
    if self._is_native:
        self._native_add_many(list(triples))
    else:
        for triple in triples:
            self.add(triple)

    from starlight.model.conformance import check_version_conformance_for_graphs
    check_version_conformance_for_graphs(
        extract_version_directive(text), [self], context='N-Triples/N-Quads document',
    )

elif format == 'trig12':
    from starlight.parsers.trig12 import parse_trig12, extract_version_directive as _trig_version
    if self._is_native:
        # Same rationale as the turtle12/longturtle12 branch
        # above - parse_trig12() returns the rdf-1.1 backend's
        # own tt:HASH encoding, which needs decoding back into
        # real TripleTerm objects before self.add() can write
        # them using the native backend's real <<( )>> syntax.
        from starlight.parsers.turtle_parser import decode_tt_encoded_triples
        skolemized = Graph()
        for triple in parse_trig12(text):
            skolemized.add(triple)
        self._native_add_many(list(decode_tt_encoded_triples(skolemized)))
    else:
        for triple in parse_trig12(text):
            super().add(triple)
        self._build_registry_from_store()

    from starlight.model.conformance import check_version_conformance_for_graphs
    check_version_conformance_for_graphs(_trig_version(text), [self], context='TriG document')

elif format == 'trix12':
    from starlight.parsers.trix12 import parse_trix12
    triples = parse_trix12(text)
    if self._is_native:
        self._native_add_many(list(triples))
    else:
        for triple in triples:
            self.add(triple)

elif format == 'rdfxml12':
    from starlight.parsers.rdfxml12 import parse_rdfxml12, extract_version_directive as _rx_version
    triples = parse_rdfxml12(text)
    if self._is_native:
        self._native_add_many(list(triples))
    else:
        for triple in triples:
            self.add(triple)

    from starlight.model.conformance import check_version_conformance_for_graphs
    check_version_conformance_for_graphs(_rx_version(text), [self], context='RDF/XML document')

elif format == 'jsonld12':
    if self._is_native:
        # super().parse() below writes straight into self's own
        # store via a bypassed rdflib-internal ConjunctiveGraph
        # wrapper (rdflib's json-ld parser's own sink, not
        # StarlightGraph.add()) - fine for the rdf-1.1 backend,
        # whose on-disk format *is* this tt:HASH encoding, but
        # wrong here: it would write the raw rdf:subject/
        # predicate/object encoding fragments directly into the
        # live native store instead of the real <<( )>> syntax
        # _native_add_many() produces, and _build_registry_from_
        # store() is a no-op for a native backend (see its own
        # docstring), so those fragments would never be
        # reconstructed - they'd leak into every later read.
        # Parsing into a throwaway plain Graph first and decoding
        # it exactly like the trig12 branch above avoids that.
        from starlight.parsers.turtle_parser import decode_tt_encoded_triples
        temp = Graph()
        temp.parse(data=text, format='json-ld')
        # rdf:type rdf:TripleTerm marker triples (see
        # starlight/serializers/jsonld12.py's own docstring for
        # this shape) aren't part of decode_tt_encoded_triples()'s
        # contract the way turtle12/trig12's own intermediate
        # sl:TripleTerm markers are (those are stripped by
        # _skolemize_encoding before decode_tt_encoded_triples
        # ever sees them) - left in place, decode_tt_encoded_
        # triples() would yield them as ordinary data with a
        # *reconstructed TripleTerm* as subject, which
        # _native_add_many() then correctly rejects (triple terms
        # aren't permitted in subject position).
        for tt_uri in list(temp.subjects(RDF.type, URIRef(_RDF_TRIPLE_TERM))):
            temp.remove((tt_uri, RDF.type, URIRef(_RDF_TRIPLE_TERM)))
        self._native_add_many(list(decode_tt_encoded_triples(temp)))
    else:
        # Delegate to rdflib's JSON-LD parser (handles @context
        # expansion); the tt: encoding triples and rdf:type
        # rdf:TripleTerm markers are loaded into the store, then
        # _build_registry_from_store rebuilds the TripleTerm
        # registry.  rdf:type rdf:TripleTerm is filtered by
        # _is_encoding_triple so it never surfaces to callers.
        super().parse(data=text, format='json-ld')
        self._build_registry_from_store()
