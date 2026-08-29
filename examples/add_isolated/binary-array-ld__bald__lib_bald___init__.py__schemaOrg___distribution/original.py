# Extracted from binary-array-ld/bald@ca59666abe : lib/bald/__init__.py
# region: schemaOrg.__distribution (lines 1489-1507, stratum add_isolated)
# licence of the source repository: see meta.json
import rdflib
import rdflib.collection
import rdflib.namespace
from bald import datetime, distribution

def __distribution(self, container, path):
    """
      Export a Schema.org distribution

      Required inputs -
          container      a bald Container URI
          path        a URI string or None


    """

    distributionNode = rdflib.BNode()
    self.__schemaGraph.add( (container, self.__so.distribution, distributionNode) )
    self.__schemaGraph.add( (distributionNode, rdflib.RDF.type, self.__so.DataDownload) )
    self.__schemaGraph.add( (distributionNode, self.__so.encodingFormat, rdflib.Literal(distribution.BaldDistributionEnum.MIME_TYPE.value)) )
    self.__schemaGraph.add( (distributionNode, self.__so.encodingFormat, rdflib.URIRef(distribution.BaldDistributionEnum.LINKED_DATA_RESOURCE_DEFINING_NETCDF.value)) )
    if path is not None:
        self.__schemaGraph.add( (distributionNode, self.__so.contentUrl, rdflib.URIRef(path)) )
    return None
