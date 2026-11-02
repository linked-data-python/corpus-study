# Context shim (see meta.json): what Entity.add_all_objects_of_type
# (IndustryFusion/DigitalTwin@3b40088b88, semantic-model/opcua/lib/entity.py)
# takes from `lib.utils` and from its class, so the method executes outside
# the repository. Identical bindings for both representations.
#
#  * NGSILD, collection_to_list and calculate_array_dimensions: copied
#    VERBATIM from semantic-model/opcua/lib/utils.py (`lib.utils` itself
#    imports pyld and much else the study venv does not have).
#  * Entity: only __init__ (without the ngsi-ld / entity-namespace
#    bookkeeping that the region does not read) -- `e` is the entity graph
#    the region fills, `basens` and `opcuans` the namespaces passed to the
#    query as initNs. The values are the ones nodeset2owl.py passes.
import operator
from functools import reduce

from rdflib import Graph, Namespace
from rdflib.collection import Collection

NGSILD = Namespace('https://uri.etsi.org/ngsi-ld/')


def calculate_array_dimensions(g, array_dimensions):
    array_length = None
    if array_dimensions is not None:
        array_length = 0
        ad = Collection(g, array_dimensions)
        if len(ad) > 0:
            array_length = reduce(operator.mul, (item.toPython() for item in ad), 1)
    return array_length


def collection_to_list(collection, datagraph: Graph, scalar_conversion=True):
    """Convert an RDF collection to a Python list."""
    if collection is None:
        return None
    ad = Collection(datagraph, collection)
    col_list = []
    if len(ad) > 0:
        if scalar_conversion:
            col_list = [item.toPython() for item in ad]
        else:
            col_list = [item for item in ad]
    return col_list


class Entity:
    def __init__(self, basens=Namespace('http://www.industry-fusion.org/base#'),
                 opcuans=Namespace('http://opcfoundation.org/UA/')):
        self.e = Graph()
        self.basens = basens
        self.opcuans = opcuans
