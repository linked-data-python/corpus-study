# Extracted from filipjezek/ndbi046@59b3a45240 : task_4/cube_lib/dimensions.py
# region: <module> (lines 1-44, stratum ns_import_project)
# licence of the source repository: see meta.json
#!/usr/bin/env python3
from rdflib import Graph, Literal, URIRef
from .namespaces import NS, NSR, RDFS, SDMX_CON, SDMX_DIM
from rdflib.namespace import QB, RDF


def create_county(collector: Graph) -> URIRef:
    county = NS.county
    collector.add((county, RDF.type, RDFS.Property))
    collector.add((county, RDF.type, QB.DimensionProperty))
    collector.add((county, RDFS.subPropertyOf, SDMX_DIM.refArea))
    collector.add((county, QB.concept, SDMX_CON.refArea))
    collector.add((county, RDFS.label, Literal('Okres', lang='cs')))
    collector.add((county, RDFS.label, Literal('County', lang='en')))
    collector.add((county, QB.codeList, NSR.county))
    collector.add((county, RDFS.range, NSR.County))
    return county


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


def create_field_of_care(collector: Graph, region: URIRef) -> URIRef:
    field_of_care = NS.fieldOfCare
    collector.add((field_of_care, RDF.type, RDFS.Property))
    collector.add((field_of_care, RDF.type, QB.DimensionProperty))
    collector.add((region, RDFS.subPropertyOf, SDMX_DIM.coverageSector))
    collector.add((region, QB.concept, SDMX_CON.coverageSector))
    collector.add((field_of_care, RDFS.label, Literal('Obor péče', lang='cs')))
    collector.add((field_of_care, RDFS.label,
                  Literal('Field of care', lang='en')))
    collector.add((field_of_care, QB.codeList, NSR.fieldOfCare))
    collector.add((field_of_care, RDFS.range, NSR.FieldOfCare))
    return field_of_care
