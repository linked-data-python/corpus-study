# Extracted from pyiron/semantikon@cfd1d3ffe5 : semantikon/analysis.py
# region: _add_child_data_class (lines 411-428, stratum sparql_literal)
# licence of the source repository: see meta.json
def _add_child_data_class(graph, label_dict):
    query_data_class = """PREFIX pmdco: <https://w3id.org/pmd/co/PMD_>
    SELECT DISTINCT ?parent ?child ?label WHERE {{
        ?parent rdfs:subClassOf ?bnode .
        ?bnode a owl:Restriction .
        ?bnode owl:onProperty bfo:0000051 .
        ?bnode owl:someValuesFrom ?child .
        ?parent rdfs:subClassOf obi:0001933 .
        ?child rdfs:subClassOf obi:0001933 .
        ?child pmdco:0000128 ?label .
    }}"""
    child_label_dict = {}
    for parent_uri, child_uri, key in graph.query(query_data_class):
        for k, v in label_dict.items():
            if v == parent_uri:
                child_label_dict[f"{k}-{key}"] = child_uri

    return label_dict | child_label_dict
