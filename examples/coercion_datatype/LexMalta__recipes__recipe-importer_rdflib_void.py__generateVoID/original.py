# Extracted from LexMalta/recipes@b861b7ccea : recipe-importer/rdflib/void.py
# region: generateVoID (lines 84-99, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, VOID

# Driver fixture: in the full function (generateVoID, not extracted here),
# `classes`/`classCount`/`classProps`/`classObjects` are computed by a first
# pass over an input graph `g` (lines 62-65 of the source file, before this
# region starts). This region is just the second pass -- a bare `for` loop
# over that data -- so it is reproduced here as plain data, faithful to the
# shapes the source builds (collections.defaultdict(set)/defaultdict(int)):
# classCount[c] and len(classes[c])/len(classProps[c])/len(classObjects[c])
# are plain ints, including a zero (class B has no distinguishing props).
classA = URIRef("http://example.org/ClassA")
classB = URIRef("http://example.org/ClassB")
dataset = URIRef("http://example.org/Dataset")
res = Graph()
classes = {
    classA: {URIRef("http://example.org/e1"), URIRef("http://example.org/e2"), URIRef("http://example.org/e3")},
    classB: {URIRef("http://example.org/e4")},
}
classCount = {classA: 5, classB: 0}
classProps = {classA: {URIRef("http://example.org/p1"), URIRef("http://example.org/p2")}, classB: set()}
classObjects = {classA: {Literal("v1")}, classB: set()}
distinctForPartitions = True

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
