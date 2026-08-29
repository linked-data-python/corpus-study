# Extracted from filipjezek/ndbi046@59b3a45240 : task_4/cube_lib/dimensions.py
# region: create_region (lines 20-30, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef
from .namespaces import NS, NSR, RDFS, SDMX_CON, SDMX_DIM
from rdflib.namespace import QB, RDF

def create_region(collector: Graph) -> URIRef:
    region = NS.region
    collector.add((region, RDF.type, RDFS.Property))
    collector.add((region, RDF.type, QB.DimensionProperty))
    collector.add((region, RDFS.subPropertyOf, SDMX_DIM.refArea))
    collector.add((region, QB.concept, SDMX_CON.refArea))
    collector.add((region, RDFS.label, Literal('Kraj', lang='cs')))
    collector.add((region, RDFS.label, Literal('Region', lang='en')))
    collector.add((region, QB.codeList, NSR.region))
    collector.add((region, RDFS.range, NSR.Region))
    return region
