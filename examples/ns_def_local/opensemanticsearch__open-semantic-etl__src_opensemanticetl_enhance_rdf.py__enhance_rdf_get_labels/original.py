# Extracted from opensemanticsearch/open-semantic-etl@f51efea6c1 : src/opensemanticetl/enhance_rdf.py
# region: enhance_rdf.get_labels (lines 32-59, stratum ns_def_local)
# licence of the source repository: see meta.json
import rdflib

def get_labels(self, subject):

    labels = []

    # append RDFS.label

    # get all labels for this obj
    for label in self.graph.objects(subject=subject, predicate=rdflib.RDFS.label):
        labels.append(str(label))

    #
    # append SKOS labels
    #

    # append SKOS prefLabel
    skos = rdflib.Namespace('http://www.w3.org/2004/02/skos/core#')
    for label in self.graph.objects(subject=subject, predicate=skos['prefLabel']):
        labels.append(str(label))

    # append SKOS altLabels
    for label in self.graph.objects(subject=subject, predicate=skos['altLabel']):
        labels.append(str(label))

    # append SKOS hiddenLabels
    for label in self.graph.objects(subject=subject, predicate=skos['hiddenLabel']):
        labels.append(str(label))

    return labels
