# Extracted from meaningfy-ws/cm2shacl@ec908f3d43 : src/cm2shacl/utils.py
# region: combine_shapes_with_same_path (lines 36-150, stratum remove)
# licence of the source repository: see meta.json
from rdflib import URIRef, BNode, RDF, SH
from collections import defaultdict
from rdflib.collection import Collection

def combine_shapes_with_same_path(graph):
    dctsource = URIRef("http://purl.org/dc/terms/source")
    dctsource_dict = defaultdict(list)

    # Collect dct:source info and remove
    for property_shapes in (graph.objects(None, SH.property),
                            graph.subjects(RDF.type, SH.PropertyShape)):
        for ps in property_shapes:
            dctsource_dict[ps].extend(graph.objects(ps, dctsource))
            graph.remove((ps, dctsource, None))

    # Find NodeShapes
    for ns in graph.subjects(RDF.type, SH.NodeShape):
        path_dict = defaultdict(list)

        # Group property shapes by path
        for ps in graph.objects(ns, SH.property):
            path = graph.value(ps, SH.path)
            if path:
                path_dict[path].append(ps)
            graph.remove((ps, SH.path, path))
            graph.remove((ns, SH.property, ps))

        # Add refined property shapes
        for path, shapes in path_dict.items():
            if len(shapes) == 1:
                graph += [(ns, SH.property, shapes[0]), (shapes[0], SH.path, path)]
                graph += [(shapes[0], dctsource, src) for src in dctsource_dict[shapes[0]]]
                continue

            # graph.remove((ps, SH.path, path))

            # Merge sh:in values
            in_values = set()
            merged_values = {SH.nodeKind: set(), SH.datatype: set(), SH["class"]: set()}
            for ps in shapes:
                for o in graph.objects(ps, SH["in"]):
                    in_values.update(graph.items(o))
                    Collection(graph, o).clear()
                    graph.remove((ps, SH["in"], o))
                for predicate, values in merged_values.items():
                    values.update(graph.objects(ps, predicate))
                    graph.remove((ps, predicate, None))

            # Create new merged shape
            merged_ps = BNode()
            # graph.add((merged_ps, RDF.type, SH.PropertyShape))

            if in_values:
                in_list = BNode()
                graph.add((merged_ps, SH["in"], in_list))
                Collection(graph, in_list, list(in_values))

            # Merge nodeKind, datatype, class using sh:or if needed
            or_shapes = []
            for predicate, values in merged_values.items():
                if len(values) == 1:
                    graph.add((merged_ps, predicate, next(iter(values))))
                else:
                    for v in values:
                        b = BNode()
                        graph.add((b, predicate, v))
                        or_shapes.append(b)

            if or_shapes:
                or_bnode = BNode()
                graph.add((merged_ps, SH["or"], or_bnode))
                Collection(graph, or_bnode, or_shapes)

            graph += [(merged_ps, SH.path, path), (ns, SH.property, merged_ps)]

            graph += [(merged_ps, dctsource, src) for ps in shapes for src in dctsource_dict[ps]]

    return graph
