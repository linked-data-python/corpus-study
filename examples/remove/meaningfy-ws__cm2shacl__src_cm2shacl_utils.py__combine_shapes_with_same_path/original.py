# Extracted from meaningfy-ws/cm2shacl@ec908f3d43 : src/cm2shacl/utils.py
# region: combine_shapes_with_same_path (lines 36-150, stratum remove)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal, BNode, RDF, RDFS, Namespace, SH
from collections import defaultdict
from rdflib.collection import Collection

def combine_shapes_with_same_path(graph):
    dctsource = URIRef("http://purl.org/dc/terms/source")
    dctsource_dict = defaultdict(list)

    # Collect dct:source info and remove
    for ps in graph.objects(None, SH.property):
        for _, _, o in graph.triples((ps, dctsource, None)):
            dctsource_dict[ps].append(o)
            graph.remove((ps, dctsource, o))
    for ps in graph.subjects(RDF.type, SH.PropertyShape):
        for _, _, o in graph.triples((ps, dctsource, None)):
            dctsource_dict[ps].append(o)
            graph.remove((ps, dctsource, o))

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
                graph.add((ns, SH.property, shapes[0]))
                graph.add((shapes[0], SH.path, path))
                for src in dctsource_dict[shapes[0]]:
                    graph.add((shapes[0], dctsource, src))
                continue

            # graph.remove((ps, SH.path, path))

            # Merge sh:in values
            in_values = set()
            nodeKinds = set()
            dataTypes = set()
            classes = set()
            for ps in shapes:
                for o in graph.objects(ps, SH["in"]):
                    for val in graph.items(o):
                        in_values.add(val)
                    collection = Collection(graph, o)
                    for item in collection:
                        pass  # Just to initialize the collection
                    collection.clear()
                    graph.remove((ps, SH["in"], o))
                for o in graph.objects(ps, SH["nodeKind"]):
                    nodeKinds.add(o)
                    graph.remove((ps, SH["nodeKind"], o))
                for o in graph.objects(ps, SH["datatype"]):
                    dataTypes.add(o)
                    graph.remove((ps, SH["datatype"], o))
                for o in graph.objects(ps, SH["class"]):
                    classes.add(o)
                    graph.remove((ps, SH["class"], o))

            # Create new merged shape
            merged_ps = BNode()
            # graph.add((merged_ps, RDF.type, SH.PropertyShape))
            graph.add((merged_ps, SH.path, path))

            if in_values:
                in_list = BNode()
                graph.add((merged_ps, SH["in"], in_list))
                in_bnode = in_list
                for val in list(in_values)[:-1]:
                    graph.add((in_bnode, RDF.first, val))
                    next_b = BNode()
                    graph.add((in_bnode, RDF.rest, next_b))
                    in_bnode = next_b
                graph.add((in_bnode, RDF.first, list(in_values)[-1]))
                graph.add((in_bnode, RDF.rest, RDF.nil))

            # Merge nodeKind, datatype, class using sh:or if needed
            or_shapes = []

            def add_or_shape(predicate, values):
                if not values:
                    return
                if len(values) == 1:
                    graph.add((merged_ps, predicate, next(iter(values))))
                else:
                    for v in values:
                        b = BNode()
                        graph.add((b, predicate, v))
                        or_shapes.append(b)

            add_or_shape(SH.nodeKind, nodeKinds)
            add_or_shape(SH.datatype, dataTypes)
            add_or_shape(SH["class"], classes)

            if or_shapes:
                or_bnode = BNode()
                graph.add((merged_ps, SH["or"], or_bnode))
                current = or_bnode
                for s in or_shapes[:-1]:
                    graph.add((current, RDF.first, s))
                    next_b = BNode()
                    graph.add((current, RDF.rest, next_b))
                    current = next_b
                graph.add((current, RDF.first, or_shapes[-1]))
                graph.add((current, RDF.rest, RDF.nil))

            graph.add((ns, SH.property, merged_ps))

            for ps in shapes:
                for src in dctsource_dict[ps]:
                    graph.add((merged_ps, dctsource, src))

    return graph
