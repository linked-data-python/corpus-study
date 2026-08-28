# Extracted from comp-int-hum/ochre-python@8392c11405 : src/pyochre/server/ochre/viewsets/ontologyviewset.py
# region: OntologyViewSet.regenerate (lines 118-161, stratum ns_def_local)
# licence of the source repository: see meta.json
from importlib.resources import files
from django.conf import settings
from rest_framework.decorators import action
from rest_framework.response import Response
from rdflib import Graph, BNode
import requests
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import OWL, RDFS

@action(detail=False, methods=["POST"])
def regenerate(self, request, pk=None):
    """
    Regenerate OCHRE ontology based on the state of the ochre.ttl file.
    """
    OCHRE = Namespace(settings.OCHRE_NAMESPACE)
    sig_string = files("pyochre").joinpath("data/ochre.ttl").read_text()

    ns = Namespace(settings.OCHRE_NAMESPACE)
    g = Graph()
    g.parse(
        data="@prefix ochre: <{}> .\n".format(settings.OCHRE_NAMESPACE) + sig_string,
        format="turtle"
    )
    from wikidata.client import Client
    client = Client()

    to_add = {}
    wikidata_descriptions = {}
    wikidata_parent_descriptions = {}
    for s, p, o in g:
        if p in [OCHRE["equivalentClass"], OCHRE["equivalentProperty"]] and "wikidata" in str(o):
            name = str(o).split("/")[-1]
            entity = client.get(name, load=True)
            if entity.data:
                wikidata_descriptions[o] = Literal(entity.description)
    for s, p, o in g:
        if p in [OCHRE["subClassOf"], OCHRE["subPropertyOf"]] and "wikidata" in str(o):
            name = str(o).split("/")[-1]
            entity = client.get(name, load=True)
            if entity.data:
                wikidata_parent_descriptions[o] = Literal(entity.description)

    for k, v in wikidata_descriptions.items():
        g.add((k, RDFS["comment"], v))
    for k, v in wikidata_parent_descriptions.items():
        g.add((k, RDFS["comment"], v))            
    resp = requests.put(
        "{}/ochre/data".format(settings.JENA_URL),
        params={"graph" : settings.ONTOLOGY_URI},
        data=g.serialize(format="text/turtle"),
        headers={"Content-type" : "text/turtle"}
    )
    return Response()
