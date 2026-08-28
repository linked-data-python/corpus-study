# Extracted from BONSAMURAIS/arborist@da18f3d17c : arborist/extract_emissions.py
# region: setup_empty_graph (lines 22-77, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal
from .graph_common import add_common_elements

def setup_empty_graph():
    global BONT, BRDFFO, BRDFLO, BRDFTIME, BRDFFAT, BRDFFOAF, BRDFDAT, BRDFPROV, dataset
    global CC, DC, DTYPE, NS0, NS1, OM2, OT, SCHEMA, TIME, XML, PROV, extent2011node

    BONT = Namespace('http://ontology.bonsai.uno/core#')
    BRDFFO = Namespace("http://rdf.bonsai.uno/flowobject/exiobase3_3_17#")
    BRDFLO = Namespace("http://rdf.bonsai.uno/location/exiobase3_3_17#")
    BRDFTIME = Namespace("http://rdf.bonsai.uno/time#")
    BRDFFAT = Namespace("http://rdf.bonsai.uno/activitytype/exiobase3_3_17#")
    BRDFFOAF = Namespace("http://rdf.bonsai.uno/foaf/bonsai#")
    BRDFDAT = Namespace("http://rdf.bonsai.uno/data/exiobase3_3_17/emission#")
    BRDFPROV = Namespace("http://rdf.bonsai.uno/prov/exiobase3_3_17#")
    CC = Namespace('http://creativecommons.org/ns#')
    DC = Namespace('http://purl.org/dc/elements/1.1/')
    DTYPE = Namespace("http://purl.org/dc/dcmitype/")
    NS0 = Namespace('http://purl.org/vocab/vann/')
    NS1 = Namespace("http://creativecommons.org/ns#")
    OM2 = Namespace('http://www.ontology-of-units-of-measure.org/resource/om-2/')
    OT = Namespace("https://www.w3.org/TR/owl-time/")
    SCHEMA = Namespace('http://schema.org/')
    TIME = Namespace('http://www.w3.org/2006/time#')
    XML = Namespace("http://www.w3.org/XML/1998/namespace")
    PROV = Namespace("http://www.w3.org/ns/prov#")

    extent2011node = URIRef("{}{}".format(BRDFTIME, '2011'))

    dataset = "http://rdf.bonsai.uno/data/exiobase3_3_17/emission"
    g = add_common_elements(
        Graph(),
        base_uri=dataset,
        title="Emission flows from Exiobase",
        description="Extracted emission flows from exiobase extensions table",
        author="BONSAI Team",
    )

    g.bind("bont", BONT)
    g.bind("brdffo", BRDFFO)
    g.bind("brdflo", BRDFLO)
    g.bind("brdftime", BRDFTIME)
    g.bind("brdffat", BRDFFAT)
    g.bind("brdfdat", BRDFDAT)
    g.bind("brdfprov", BRDFPROV)
    g.bind("bfoaf", BRDFFOAF)
    g.bind("cc", CC)
    g.bind("dc", DC)
    g.bind("dtype", DTYPE)
    g.bind("ns0", NS0)
    g.bind("ns1", NS1)
    g.bind("om2", OM2)
    g.bind("ot", OT)
    g.bind("schema", SCHEMA)
    g.bind("time", TIME)
    g.bind("xml", XML)
    g.bind("prov", PROV)

    return g
