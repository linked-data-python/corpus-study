# Extracted from IBM/kif@4ce99d0d9b : kif_lib/codec/sparql/decoder.py
# region: SPARQL_Decoder.decode (lines 74-139, stratum bind_initbindings)
# licence of the source repository: see meta.json
from rdflib.paths import Path
from rdflib.plugins.sparql import prepareQuery
from rdflib.term import Identifier as Id
from rdflib.term import Literal, URIRef, Variable
from ...model import (
    AndFingerprint,
    Filter,
    Fingerprint,
    Property,
    Snak,
    Value,
    ValueFingerprint,
    ValueSnak,
)
from ...typing import Any, cast, override

@override
def decode(self, input: str) -> Any:
    from pyparsing.exceptions import ParseException
    try:
        query = prepareQuery(input, initNs=self._namespace)
    except ParseException as err:
        raise self._error_bad_query(
            input, err.lineno, err.column, err.explain())
    fpmap: dict[Variable, list[Snak]] = {}
    snmap: dict[ValueSnak, tuple[Id, Id]] = {}
    subj: Id | None = None
    pred: Id | None = None
    obj: Id | None = None
    for (s, p, o) in self._get_bgp_triples(query.algebra):
        if (isinstance(s, Variable)
            and isinstance(p, URIRef)
                and isinstance(o, (URIRef, Literal))):
            if s not in fpmap:
                fpmap[s] = []
            assert isinstance(p, URIRef)
            sp = self._uriref_to_property(p)
            if isinstance(o, URIRef):
                sv: Value = self._uriref_to_value(o)
            elif isinstance(o, Literal):
                sv = self._literal_to_value(o)
            else:
                raise self._should_not_get_here()
            snak = ValueSnak(sp, sv)
            snmap[snak] = (p, o)
            fpmap[s].append(snak)
        elif isinstance(p, Path):
            continue        # skip: property path
        else:
            subj = s
            if not isinstance(s, (URIRef, Variable)):
                raise self._error_unsupported_bgp(
                    f"bad subject ({s})")
            pred = p
            if not isinstance(s, (URIRef, Variable)):
                raise self._error_unsupported_bgp(
                    f"bad predicate ({p})")
            obj = o
            if not isinstance(s, (URIRef, Literal, Variable)):
                raise self._error_unsupported_bgp(
                    f"bad object ({o})")
    if subj is None and pred is None and obj is None:
        if not fpmap:
            return Filter(None, None, None, 0)
        else:
            assert len(fpmap) == 1
            snaks = list(fpmap.values())[0]
            assert len(snaks) > 0
            if len(snaks) > 1:
                subj = list(fpmap.keys())[0]
            else:
                ###
                # If it is a single triple, do the right thing, i.e.,
                # returns the filter Filter(s, p, o).
                ###
                subj = None
                pred, obj = snmap[cast(ValueSnak, snaks[0])]
    return Filter(
        self._subject_to_fingerprint(subj, fpmap),
        self._predicate_to_fingerprint(pred, fpmap),
        self._object_to_fingerprint(obj, fpmap)
    )
