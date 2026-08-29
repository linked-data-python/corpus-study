# Extracted from filipjezek/ndbi046@59b3a45240 : task_4/population_dataset.py
# region: create_dataset_entry (lines 26-57, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCAT, RDF, DCTERMS, RDFS
from cube_lib.namespaces import NSR

def create_dataset_entry(collector: Graph):
    collector.add((NSR.PopulationDataCube, RDF.type, DCAT.Dataset))
    collector.add((NSR.PopulationDataCube, DCTERMS.title,
                  Literal('Population data cube', lang='en')))
    collector.add((NSR.PopulationDataCube, RDFS.label,
                  Literal('Population data cube', lang='en')))
    collector.add((NSR.PopulationDataCube, DCTERMS.description, Literal(
        'A data cube containing mean population of Czech counties and regions in 2021', lang='en')))
    collector.add((NSR.PopulationDataCube, DCTERMS.spatial, URIRef(
        'http://publications.europa.eu/resource/authority/country/CZE')))
    collector.add((NSR.PopulationDataCube, DCTERMS.accrualPeriodicity, URIRef(
        'http://publications.europa.eu/resource/authority/frequency/NEVER')))
    me = URIRef('https://github.com/filipjezek')
    collector.add((NSR.PopulationDataCube, DCTERMS.publisher, me))
    collector.add((NSR.PopulationDataCube, DCTERMS.creator, me))
    collector.add((NSR.PopulationDataCube, DCAT.keyword,
                  Literal('population', lang='en')))
    collector.add((NSR.PopulationDataCube, DCAT.keyword,
                  Literal('region', lang='en')))
    collector.add((NSR.PopulationDataCube, DCAT.keyword,
                  Literal('district', lang='en')))
    collector.add((NSR.PopulationDataCube, DCAT.theme,
                  URIRef('http://eurovoc.europa.eu/2908')))

    distribution = NSR['PopulationDataCube.ttl']
    collector.add((NSR.PopulationDataCube, DCAT.distribution, distribution))
    collector.add((distribution, RDF.type, DCAT.Distribution))
    collector.add((distribution, DCAT.accessURL, distribution))
    collector.add((distribution, DCTERMS.format, URIRef(
        'http://publications.europa.eu/resource/authority/file-type/RDF_TURTLE')))
    collector.add((distribution, DCAT.mediaType, URIRef(
        'http://www.iana.org/assignments/media-types/text/turtle')))
