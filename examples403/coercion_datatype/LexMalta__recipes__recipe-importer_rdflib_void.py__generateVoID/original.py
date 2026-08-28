# Extracted from LexMalta/recipes@b861b7ccea : recipe-importer/rdflib/void.py
# region: generateVoID (lines 84-99, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, VOID

for i, c in enumerate(classes):
    part = URIRef(dataset + "_class%d" % i)
    res.add((dataset, VOID.classPartition, part))
    res.add((part, RDF.type, VOID.Dataset))

    res.add((part, VOID.triples, Literal(classCount[c])))
    res.add((part, VOID.classes, Literal(1)))

    res.add((part, VOID["class"], c))

    res.add((part, VOID.entities, Literal(len(classes[c]))))
    res.add((part, VOID.distinctSubjects, Literal(len(classes[c]))))

    if distinctForPartitions:
        res.add((part, VOID.properties, Literal(len(classProps[c]))))
        res.add((part, VOID.distinctObjects, Literal(len(classObjects[c]))))
