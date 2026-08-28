# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/shacl2flink/lib/shacl_properties_to_sql.py
# region: translate (lines 2209-2209, stratum bind_initbindings)
# licence of the source repository: see meta.json
import lib.utils as utils
sparql_get_all_properties = """
SELECT
    ?nodeshape ?targetclass ?inheritedTargetclass ?propertypath ?mincount ?maxcount ?attributeclass ?nodekind
    ?minexclusive ?maxexclusive ?mininclusive ?maxinclusive ?minlength ?maxlength ?pattern ?severitycode ?property ?valuepath ?innerOr ?hasValue ?connective ?ownparams ?clause ?innerconnective
    (GROUP_CONCAT(CONCAT('"', ?in, '"'); separator=',') as ?ins)
    (GROUP_CONCAT(?datatype; separator=',') as ?datatypes)
where {
    ?nodeshape a sh:NodeShape .
    ?nodeshape sh:targetClass ?targetclass .
    ?inheritedTargetclass rdfs:subClassOf* ?targetclass .
    ?nodeshape (sh:property|(sh:or|sh:and|sh:xone)/rdf:rest*/rdf:first|sh:not)+ ?property .
      ## First-level property. sh:or, sh:and and sh:xone are all an RDF list of
      ## shapes, so one pattern covers them; ?connective carries which it was.
  ?property sh:path ?propertypath .
    { VALUES ?connective { sh:or sh:and sh:xone }
      ?property ?connective ?outerOr .
      ?outerOr rdf:rest*/rdf:first ?clause . }
    UNION
    { BIND(sh:not AS ?connective)
      ?property sh:not ?clause . }
    UNION
    ## The property node's OWN parameters. They are conjoined with any
    ## connective, never a member of it, so they are collected under a separate
    ## group (?ownparams) and published as an independent constraint. When there
    ## is no connective at all this is the only arm that matches, and the node
    ## simply IS the clause -- which is what a shape looks like as written. The
    ## former normalisation pass existed only to wrap that in a singleton sh:or
    ## so the two patterns above could match it.
    ## NOTE: ?property must be re-bound INSIDE the arm. UNION arms are evaluated
    ## independently of the patterns preceding them, so a FILTER here would
    ## otherwise see ?property unbound and match every triple in the graph.
    { ?property sh:path ?propertypath .
      FILTER EXISTS { ?property (sh:minCount|sh:maxCount|sh:nodeKind|sh:property) ?ownparam }
      BIND(?property AS ?clause)
      BIND(true AS ?ownparams) }
    OPTIONAL { ?clause  sh:minCount ?mincount ; }
    OPTIONAL { ?clause sh:maxCount ?maxcount ; }
    OPTIONAL { ?clause sh:severity ?severity . ?severity rdfs:label ?severitycode .}
    ?clause     sh:property    ?innerProp .
    ## Same three cases again one level down, for the value shape. Its
    ## connective gets its own circuit node rather than being folded into the
    ## property's -- see the two-level grouping in translate().
    { VALUES ?innerconnective { sh:or sh:and sh:xone }
      ?innerProp sh:path ?valuepath ;
          ?innerconnective   ?innerOr .
      ?innerOr rdf:rest*/rdf:first ?innerclause . }
    UNION
    { BIND(sh:not AS ?innerconnective)
      ?innerProp sh:path ?valuepath ;
          sh:not ?innerclause . }
    UNION
    { ?innerProp sh:path ?valuepath .
      FILTER NOT EXISTS { ?innerProp (sh:or|sh:and|sh:xone|sh:not) ?anyinnerconnective }
      BIND(?innerProp AS ?innerclause) }
    FILTER(?valuepath = ngsi-ld:hasValue || ?valuepath = ngsi-ld:hasValueList || ?valuepath = ngsi-ld:hasJSON)
    ## Value parameters may sit on the value shape itself or on the branch of a
    ## connective inside it -- `sh:nodeKind sh:Literal` beside `sh:or (datatype
    ## a) (datatype b)` is the common case. Both are read: the branch binds
    ## first and the value shape fills in whatever the branch did not set, so a
    ## parameter written next to a connective is never lost.
    OPTIONAL { ?innerclause sh:minExclusive ?minexclusive ; }
    OPTIONAL { ?innerProp   sh:minExclusive ?minexclusive ; }
    OPTIONAL { ?innerclause sh:maxExclusive ?maxexclusive ; }
    OPTIONAL { ?innerProp   sh:maxExclusive ?maxexclusive ; }
    OPTIONAL { ?innerclause sh:minInclusive ?mininclusive ; }
    OPTIONAL { ?innerProp   sh:minInclusive ?mininclusive ; }
    OPTIONAL { ?innerclause sh:maxInclusive ?maxinclusive ; }
    OPTIONAL { ?innerProp   sh:maxInclusive ?maxinclusive ; }
    OPTIONAL { ?innerclause sh:minLength ?minlength ; }
    OPTIONAL { ?innerProp   sh:minLength ?minlength ; }
    OPTIONAL { ?innerclause sh:maxLength ?maxlength ; }
    OPTIONAL { ?innerProp   sh:maxLength ?maxlength ; }
    OPTIONAL { ?innerclause sh:pattern ?pattern ; }
    OPTIONAL { ?innerProp   sh:pattern ?pattern ; }
    OPTIONAL { ?innerclause sh:in/(rdf:rest*/rdf:first)+ ?in ; }
    OPTIONAL { ?innerProp   sh:in/(rdf:rest*/rdf:first)+ ?in ; }
    OPTIONAL { ?innerclause sh:hasValue ?hasValue ; }
    OPTIONAL { ?innerProp   sh:hasValue ?hasValue ; }
    OPTIONAL { ?innerclause sh:class ?attributeclass ; }
    OPTIONAL { ?innerProp   sh:class ?attributeclass ; }
    OPTIONAL { ?innerclause sh:nodeKind ?nodekind ; }
    OPTIONAL { ?innerProp   sh:nodeKind ?nodekind ; }
    OPTIONAL { ?innerclause sh:or/rdf:rest*/rdf:first ?dtShape  . ?dtShape sh:datatype ?datatype .}
    OPTIONAL { ?innerclause sh:property/sh:or/rdf:rest*/rdf:first ?dtShape  . ?dtShape sh:datatype ?datatype .}
    OPTIONAL { ?innerclause sh:datatype ?datatype ; }
    OPTIONAL { ?innerProp   sh:datatype ?datatype ; }
    ## The datatype of a LIST ELEMENT. It sits on a nested sh:property whose
    ## sh:path is a path EXPRESSION -- ([sh:zeroOrMorePath rdf:rest] rdf:first)
    ## -- rather than a plain predicate, which is what distinguishes it from a
    ## sub-attribute. Without these two arms the element datatype never reached
    ## constraint_table at all, so "a list of integers" compiled to "is a JSON
    ## array" and a list of strings satisfied it.
    OPTIONAL { ?innerclause sh:property ?elemShape . ?elemShape sh:path ?elemPath .
               FILTER(isBlank(?elemPath)) . ?elemShape sh:datatype ?datatype . }
    OPTIONAL { ?innerProp   sh:property ?elemShape . ?elemShape sh:path ?elemPath .
               FILTER(isBlank(?elemPath)) . ?elemShape sh:datatype ?datatype . }
}
GROUP BY ?nodeshape ?targetclass ?propertypath ?mincount ?maxcount ?attributeclass ?nodekind
    ?minexclusive ?maxexclusive ?mininclusive ?maxinclusive ?minlength ?maxlength ?pattern ?severitycode ?inheritedTargetclass ?property ?valuepath ?innerOr ?hasValue ?connective ?ownparams ?clause ?innerconnective
order by ?inheritedTargetclass
"""  # noqa: E501

qres = utils.in_stable_order(g.query(sparql_get_all_properties, initNs=prefixes))
