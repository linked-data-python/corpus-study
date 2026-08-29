# Extracted from filipjezek/ndbi046@59b3a45240 : task_3/population_provenance.py
# region: PopulationProv.__init__ (lines 33-54, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef, BNode
from cube_lib.namespaces import NS, NSR

def __init__(self):
    self.__collector = Graph()
    self.__me = URIRef('https://github.com/filipjezek')
    self.__cube = NSR.PopulationDataCube
    self.__preprocessed = NSR.PreprocessedPopulationData
    self.__script = NSR.PopulationScript
    self.__county_script = NSR.CountyTransformationScript
    self.__datasrc = URIRef(
        'https://www.czso.cz/documents/10180/184344914/130141-22data2021.csv')
    self.__countysrc = URIRef(
        'https://skoda.projekty.ms.mff.cuni.cz/ndbi046/seminars/02/číselník-okresů-vazba-101-nadřízený.csv')
    self.__org = URIRef('https://mff.cuni.cz')
    self.__czso = URIRef('https://www.czso.cz')
    self.__skoda = URIRef('https://skodapetr.github.io')
    self.__county_conversion = NSR.CountyConversion
    self.__transformation = NSR.PopulationTransformation
    self.__role_raw_data = NSR.roleRawData

    self.__add_activities()
    self.__add_agents()
    self.__add_entities()
    self.__add_roles()
