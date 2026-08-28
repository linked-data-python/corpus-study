"""Context shim (see meta.json) for `kgcl_rdflib.apply.graph_transformer`.

`apply_patch` is reproduced from INCATools/kgcl-rdflib@7af638bbd7
(kgcl_rdflib/apply/graph_transformer.py) and the SPARQL UPDATE it runs for a
node rename is reproduced from the same commit's
kgcl_rdflib/apply/kgcl_2_sparql.py:rename(), restricted to the IRI /
no-language case used by the demo harness.  Imported IDENTICALLY by
original.py and translated.ldpy.
"""

import logging


def convert(kgcl_instance):
    """SPARQL UPDATE for a NodeRename (kgcl_2_sparql.rename, IRI subject)."""
    old_value = kgcl_instance.old_value[1:-1]
    new_value = kgcl_instance.new_value[1:-1]
    subject = kgcl_instance.about_node

    prefix = "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>"
    delete = "DELETE {" + subject + " rdfs:label ?oldlabel .}"
    insert = "INSERT {" + subject + " rdfs:label ?newlabel .}"
    where_query = subject + " rdfs:label ?label .  "
    where_query += ' FILTER(STR(?label)="' + old_value + '") '
    where_query += ' BIND("' + old_value + '" AS ?oldlabel) '
    where_query += ' BIND("' + new_value + '" AS ?newlabel) '
    where = "WHERE {" + where_query + "}"
    return prefix + " " + delete + " " + insert + " " + where


def apply_patch(kgcl_instances, graph):
    """Apply patch."""
    for i in kgcl_instances:
        query = convert(i)
        logging.info(f"Query: {query}")
        graph.update(query)
