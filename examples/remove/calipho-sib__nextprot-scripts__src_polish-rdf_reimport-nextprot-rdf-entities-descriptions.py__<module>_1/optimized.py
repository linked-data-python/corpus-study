# Extracted from calipho-sib/nextprot-scripts@f03504ce5e : src/polish-rdf/reimport-nextprot-rdf-entities-descriptions.py
# region: <module> (lines 1-112, stratum remove)
# licence of the source repository: see meta.json
import rdflib
from rdflib import URIRef, Literal
from rdflib.namespace import Namespace
from rdflib.namespace import XSD
import sys

# input file with possibly new labels and new comments
goofiles= [
    "nextprot-rdf-classes - nextprot-rdf-classes-V2.tsv",
    "nextprot-rdf-classes - nextprot-rdf-predicates.tsv",
    "nextprot-rdf-classes - nextprot-named-individuals.tsv"
    ]

# input file with current schema in ttl format
ttlfile="schema.ttl"

# output file
new_ttlfile = "schema-new.ttl"

# load graph from current schema.ttl file
print("### Reading and loading current graph schema", ttlfile)
g = rdflib.Graph()
g.parse(ttlfile)
print("### Graph triple count before changes", len(g))

# save initial step
g.serialize(destination = "schema-tmp.0")

for step, goofile in enumerate(goofiles, 1):
    # get changes from google doc sheet TAB
    print("### Reading changes to do in file", goofile)
    entities_to_hide = set()
    entities_to_change = dict()
    with open(goofile) as f_in:
        while True:
            line = f_in.readline()
            if line == "": break
            # skip lines not related to a specific class URI
            if not line.startswith("http://nextprot.org/rdf"): continue
            uri, name, status, label, new_label, comment, new_comment = (
                field.strip() for field in line.split("\t")[:7])

            # entities we will remove from the schema
            if status.lower() == "private":
                entities_to_hide.add(uri)
            # check the current uri appears as a subject in the graph
            # unknown entities we should not have in the goo files
            elif (URIRef(uri), None, None) not in g:
                print("### Unknown uri", uri)
            # entities to be updated
            else:
                entities_to_change[uri] = {"uri": uri, "name": name , "label": label,
                      "new_label": new_label, "comment": comment, "new_comment": new_comment }

    # remove entities that should not appear in ontology
    for k in entities_to_hide:
        print("### Removing any triple related to", k)
        g.remove((URIRef(k), None, None))
        g.remove((None, None, URIRef(k)))
    print("### Graph triple after removals", len(g))

    # update label and comments according to content of google doc
    for k, record in entities_to_change.items():
        g.remove((URIRef(k), rdflib.RDFS.label, None))
        g.remove((URIRef(k), rdflib.RDFS.comment, None))
        label, new_label = record["label"], record["new_label"]
        if label != new_label: print("### Label change in google doc", k, label, "=>", new_label)
        if new_label:
            g.add((URIRef(k), rdflib.RDFS.label, Literal(new_label, datatype=XSD.string)))
        comment, new_comment = record["comment"], record["new_comment"]
        if comment != new_comment: print("### Comment change in google doc", k , comment, "=>", new_comment)
        if new_comment:
            g.add((URIRef(k), rdflib.RDFS.comment, Literal(new_comment, datatype=XSD.string)))
    print("### Graph triple after all changes", len(g))

    g.serialize(destination = f"schema-tmp.{step}")

# now save new schame in a new file
print("### Saving modified schema", new_ttlfile)
g.serialize(destination = new_ttlfile)

print("### end")
