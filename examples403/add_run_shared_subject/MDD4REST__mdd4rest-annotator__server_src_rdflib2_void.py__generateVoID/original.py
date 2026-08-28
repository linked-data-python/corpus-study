# Extracted from MDD4REST/mdd4rest-annotator@c46839aa3d : server/src/rdflib2/void.py
# region: generateVoID (lines 82-99, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import URIRef, Graph, Literal
from rdflib.namespace import VOID, RDF

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
        res.add(
            (part, VOID.properties, Literal(len(classProps[c]))))
        res.add((part, VOID.distinctObjects,
                Literal(len(classObjects[c]))))
