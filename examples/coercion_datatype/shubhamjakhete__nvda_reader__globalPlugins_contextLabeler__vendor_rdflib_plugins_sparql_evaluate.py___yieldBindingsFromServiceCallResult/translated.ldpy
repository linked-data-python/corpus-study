# Extracted from shubhamjakhete/nvda_reader@8b5fb51e42 : globalPlugins/contextLabeler/_vendor/rdflib/plugins/sparql/evaluate.py
# region: _yieldBindingsFromServiceCallResult (lines 414-440, stratum coercion_datatype)
# licence of the source repository: see meta.json
from typing import (
    TYPE_CHECKING,
    Any,
    Deque,
    Dict,
    Generator,
    Iterable,
    List,
    Mapping,
    Optional,
    Tuple,
    Union,
)
from rdflib.plugins.sparql.sparql import (
    AlreadyBound,
    FrozenBindings,
    FrozenDict,
    Query,
    QueryContext,
    SPARQLError,
)
from rdflib.term import BNode, Identifier, Literal, URIRef, Variable

def _yieldBindingsFromServiceCallResult(
    ctx: QueryContext, r: Dict[str, Dict[str, str]], variables: List[str]
) -> Generator[FrozenBindings, None, None]:
    res_dict: Dict[Variable, Identifier] = {}
    for var in variables:
        if var in r and r[var]:
            var_binding = r[var]
            var_type = var_binding["type"]
            if var_type == "uri":
                res_dict[Variable(var)] = URIRef(var_binding["value"])
            elif var_type == "literal":
                res_dict[Variable(var)] = Literal(
                    var_binding["value"],
                    datatype=var_binding.get("datatype"),
                    lang=var_binding.get("xml:lang"),
                )
            # This is here because of
            # https://www.w3.org/TR/2006/NOTE-rdf-sparql-json-res-20061004/#variable-binding-results
            elif var_type == "typed-literal":
                res_dict[Variable(var)] = Literal(
                    var_binding["value"], datatype=URIRef(var_binding["datatype"])
                )
            elif var_type == "bnode":
                res_dict[Variable(var)] = BNode(var_binding["value"])
            else:
                raise ValueError(f"invalid type {var_type!r} for variable {var!r}")
    yield FrozenBindings(ctx, res_dict)
