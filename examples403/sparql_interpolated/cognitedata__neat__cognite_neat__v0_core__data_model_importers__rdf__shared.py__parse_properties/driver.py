"""Validation driver for
cognitedata__neat__cognite_neat__v0_core__data_model_importers__rdf__shared.py__parse_properties.

IDENTITY translation (see meta.json): `query` is a whole SPARQL query STRING
passed in by the caller -- `parse_properties` is a generic helper, reused by
every RDF-based importer with a *different* query -- and only `.format
(language=language)` before `prepareQuery(...)`. `s{ }` is written as a
literal island in the ldpy SOURCE, validated at transpile time (querying.md);
there is no mechanism to hand it a query held in a runtime string, so a
function generic over an arbitrary caller-supplied query cannot be expressed
by any island regardless of what that query itself contains.

This region READS a graph, so the oracle is the equality of the values both
versions produce from the same input (design record corpus/403 SS3). The
real caller is `OWLImporter._to_data_model_components` (cognite/neat/_v0/
core/_data_model/importers/_rdf/_owl2data_model.py, at the pinned commit):
this driver reuses its real PROPERTIES_QUERY and PROPERTIES_QUERY_PARAMETERS
verbatim, rather than inventing a query of our own.

`parse_properties(graph, query, parameters, language, issue_list)` takes
five arguments (not the one `fixture=` alone would pass), so `calls=` is
built by hand with `fixture_graph()`:

  * fixture.ttl -- several solutions (ex:hasAge: a plain positive case;
    ex:hasTag: two ranges on one property, folding into one grouped entry
    with a multi-value value_type list; ex:hasQuietFlag: no label/comment at
    all, both stay None), a blank-node ?concept and a blank-node ?value_type
    (each hits one of parse_properties's own BNode-skip branches), and
    neighbourhood that must not match the query's own property-type FILTER
    or isn't a property at all (see fixture.ttl for all of the above);
  * fixture_empty.ttl -- the zero-solution case: no owl:ObjectProperty/
    owl:DatatypeProperty resource at all, so `properties` stays empty and
    NeatValueError("Unable to parse properties") is appended to issue_list.

`issue_list` is passed in fresh (an empty neat_shared_context.IssueList())
per call, per side, so a warning appended on one side cannot leak into the
other's input.
"""
from pathlib import Path

from rdfeval.harness import fixture_graph, run_pair
from neat_shared_context import IssueList

HERE = Path(__file__).resolve().parent

# Verbatim from cognite/neat/_v0/core/_data_model/importers/_rdf/_owl2data_model.py
# (OWLImporter, the real -- and only -- caller of parse_properties).
PROPERTIES_QUERY = """ SELECT ?concept ?property_ ?name ?description ?value_type ?min_count ?max_count ?default
    WHERE {{
        ?property_ a ?property_Type.
        FILTER (?property_Type IN (owl:ObjectProperty, owl:DatatypeProperty ) )

        # --- 1. Explicit Domain Discovery ---

        # A. Handling owl:domain when it is expressed as owl restriction
        OPTIONAL {{
            ?property_ rdfs:domain ?domain_exp_node .
            FILTER(isBlank(?domain_exp_node))
            ?domain_exp_node owl:unionOf|owl:intersectionOf ?exp_concepts_list .
            ?exp_concepts_list rdf:rest*/rdf:first ?explicit_concept.
        }}

        # B. Handling the domain when it is a single concept
        OPTIONAL {{
            ?property_ rdfs:domain ?domain_exp_node .
            FILTER(!isBlank(?domain_exp_node))
            BIND(?domain_exp_node AS ?explicit_concept)
        }}

        # --- 2. Inherited Domain Discovery (Fallback) ---

        # C. Handling inherited domain when parent domain is a restriction
        OPTIONAL {{
            ?property_ rdfs:subPropertyOf ?parent_property .
            ?parent_property rdfs:domain ?parent_domain_node .
            FILTER(isBlank(?parent_domain_node))
            ?parent_domain_node owl:unionOf|owl:intersectionOf ?parent_concepts_list .
            ?parent_concepts_list rdf:rest*/rdf:first ?inherited_concept.
        }}

        # D. Handling inherited domain when parent domain is a single concept
        OPTIONAL {{
            ?property_ rdfs:subPropertyOf ?parent_property .
            ?parent_property rdfs:domain ?parent_domain_node .
            FILTER(!isBlank(?parent_domain_node))
            BIND(?parent_domain_node AS ?inherited_concept)
        }}

        # Final Concept Assignment with Priority ---
        # COALESCE prioritizes ?explicit_concept over ?inherited_concept
        BIND(COALESCE(?explicit_concept, ?inherited_concept) AS ?concept)


        # Handling owl:range when it is expressed as owl restriction
        OPTIONAL {{
            ?property_ rdfs:range ?range .
            FILTER(isBlank(?range))
            ?range owl:unionOf|owl:intersectionOf ?value_types .
            ?value_types rdf:rest*/rdf:first ?value_type.
        }}

        # Handling the range when it is a single concept
        OPTIONAL {{
            ?property_ rdfs:range ?range .
            FILTER(!isBlank(?range))
            BIND(?range AS ?value_type)
        }}

        OPTIONAL {{?property_ rdfs:label|skos:prefLabel ?name }}.
        OPTIONAL {{?property_ rdfs:comment|skos:definition ?description}}.
        OPTIONAL {{?property_ owl:maxCardinality ?max_count}}.
        OPTIONAL {{?property_ owl:minCardinality ?min_count}}.

        # FILTERS
        FILTER (!isBlank(?property_))
        FILTER (!bound(?name) || LANG(?name) = "" || LANGMATCHES(LANG(?name), "{language}"))
        FILTER (!bound(?description) || LANG(?description) = "" || LANGMATCHES(LANG(?description), "{language}"))
    }}
    """
PROPERTIES_QUERY_PARAMETERS = {
    "concept",
    "property_",
    "name",
    "description",
    "value_type",
    "min_count",
    "max_count",
    "default",
}


def _call(fixture_name):
    def make():
        graph = fixture_graph(HERE / fixture_name)
        return (
            (graph, PROPERTIES_QUERY, PROPERTIES_QUERY_PARAMETERS, "en", IssueList()),
            {},
        )
    return make


VERDICT = run_pair(
    __file__,
    entry="parse_properties",
    calls=[
        _call("fixture.ttl"),        # several solutions, both BNode-skip branches
        _call("fixture_empty.ttl"),  # zero solutions -> NeatValueError appended
    ],
    # Hand-built calls= (parse_properties takes five arguments, not the one
    # fixture= alone would pass), so ordered does not default to False on
    # its own: no store promises a row order, and `properties` is a plain
    # dict keyed by "concept.property_" -- comparing it as a value already
    # ignores row order; explicit here for the same reason the sibling
    # bind_initbindings drivers are explicit.
    ordered=False,
)
