# Extracted from Mat-O-Lab/RDFConverter@0d81f4d1ba : app.py
# region: apply_mapping (lines 1473-1546, stratum trav_single_value)
# licence of the source repository: see meta.json
#
# The extracted region is a mid-method statement block: `duplicate_for_table`,
# `is_rdf_data`, `rows`, `template_url`, `template_content`, `template_graph`,
# `data_graph`, `mapping_graph` and `joined_graph` are locals computed earlier
# in `apply_mapping` (one of the 163 regions with no visible graph, see
# AGENT_BATCH.md). Restored below as a minimal fixture that drives the
# `if duplicate_for_table and ...:` branch — the one under study — through
# both a matched read (`propertyUrl` present, a joined-graph lookup that
# hits) and an unmatched one (no `propertyUrl`, falls back to the column
# itself; a joined-graph lookup that misses). `strip_namespace` is imported
# from rmlmapper_shim.py (see meta.json) rather than the real rmlmapper
# module, which pulls in a live HTTP client unrelated to this region.
import logging
from rdflib import Graph, Namespace, URIRef, BNode, Literal
from rdflib.namespace import CSVW, RDF, RDFS, PROV, XSD
from rmlmapper_shim import count_rules_str, replace_data_source, replace_all_data_sources, strip_namespace
CSVW = Namespace("http://www.w3.org/ns/csvw#")

EX = Namespace("http://example.org/")

duplicate_for_table = True
is_rdf_data = True
template_graph = None

data_graph = Graph()
data_graph.add((EX.tg, RDF.type, CSVW.TableGroup))
data_graph.add((EX.col1, RDF.type, CSVW.Column))
data_graph.add((EX.col1, CSVW.propertyUrl, EX.propA))
data_graph.add((EX.col2, RDF.type, CSVW.Column))  # no propertyUrl: next(..., default) falls back to the column itself
data_graph.add((EX.row1, RDF.type, CSVW.Row))
data_graph.add((EX.row1, CSVW.describes, EX.node1))
data_graph.add((EX.node1, EX.propA, Literal("valA1")))

mapping_graph = Graph()
mapping_graph.add((EX.col1, EX.hasType, EX.SomeType))
mapping_graph.add((EX.col2, EX.hasLabel, Literal("Foo")))
mapping_graph.add((EX.note1, EX.hasComment, Literal("hello")))  # a non-column subject

rows = [EX.row1]

template_url = "TEMPLATE_URL_PLACEHOLDER"
template_content = f"<{template_url}/label> a <http://example.org/Thing> ."

joined_graph = Graph()
if is_rdf_data:
    joined_graph += data_graph

if duplicate_for_table and is_rdf_data and rows and template_url and template_content:
    # map_content=mapping_graph.serialize()
    # mapping_graph.serialize("map_graph.ttl")
    # data_graph.serialize("data_graph.ttl")
    tablegroup = next(data_graph[: RDF.type : CSVW.TableGroup])
    column_maps = {}
    for column in data_graph[: RDF.type : CSVW.Column]:
        column_maps[column] = {
            "po": list(mapping_graph.predicate_objects(subject=column)),
            "propertyUrl": next(
                data_graph.objects(subject=column, predicate=CSVW.propertyUrl),
                column,
            ),
        }
    non_column_subjects = [
        subject
        for subject in mapping_graph.subjects(unique=True)
        if subject not in column_maps.keys()
    ]
    note_maps = {
        note: {"po": list(mapping_graph.predicate_objects(note))}
        for note in non_column_subjects
    }
    for_row_to_set = list()

    # adding tripples for columns
    print("column_map:{}".format(column_maps))
    for column, data in column_maps.items():
        print(column, data)
        property = data["propertyUrl"]
        for predicate, object in data["po"]:
            for_row_to_set.append(
                (property, predicate, strip_namespace(str(object)))
            )
    print("to set for row: {}".format(for_row_to_set))

    # adding tripples for notes
    for_copy_to_set = list()
    for note, data in note_maps.items():
        for predicate, object in data["po"]:
            for_copy_to_set.append((note, predicate, strip_namespace(str(object))))

    # print(for_copy_to_set)
    logging.info("dublicating template graph for {} rows".format(len(rows)))
    for row in rows:
        data_node = data_graph.value(row, CSVW.describes)
        if template_url and template_content:
            joined_graph.parse(
                data=template_content.replace(template_url, data_node + "/")
            )
        row_ns = Namespace(data_node + "/")
        joined_graph.bind("row" + str(data_node).rsplit("-", 1)[-1], row_ns)
        # set mapping realtions on each individual row
        for property, predicate, object in for_row_to_set:
            subject = next(joined_graph.objects(data_node, property), None)
            if subject:
                joined_graph.add((subject, predicate, row_ns[object]))
        for subject, predicate, object in for_copy_to_set:
            joined_graph.add((subject, predicate, row_ns[object]))

else:
    # Join graphs based on what's available
    if template_graph and template_content:
        # Parse template AS IS (don't replace namespace yet - it causes file:///src/ issue!)
        temp_template_graph = Graph()
        temp_template_graph.parse(data=template_content)
        joined_graph += temp_template_graph

    joined_graph += mapping_graph

    # Only add data_graph if the data source was RDF
    # For plain JSON, RML rules generate all needed triples
    if is_rdf_data:
        joined_graph += data_graph
