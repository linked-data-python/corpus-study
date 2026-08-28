# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/lib/shacl.py
# region: Shacl.get_array_validation_shape (lines 90-144, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, SH, split_uri
from rdflib.collection import Collection
from functools import reduce
import operator

def get_array_validation_shape(self, datatype, pattern, value_rank, array_dimensions):
    """Create Shape for Array
       Example: "@list": [1] is translated to RDF like a linked list:
                 _:b0 rdf:first 1 ;
                 rdf:rest rdf:nil .
                 So the corresponding SHACL expression is
                [
                  sh:property [ sh:or ( [ sh:datatype xsd:integer ] ) ;
                    sh:path ( [ sh:zeroOrMorePath rdf:rest ] rdf:first ) ] ]
    Args:
        datatype (_type_): _description_
        pattern (_type_): _description_
        value_rank (_type_): _description_
        array_dimensions (_type_): _description_

    Returns:
        _type_: _description_
    """
    property_shape = BNode()
    zero_or_more_node = BNode()
    self.shaclg.add((zero_or_more_node, SH.zeroOrMorePath, RDF.rest))
    path_list_head = BNode()
    # The list items: first element is zero_or_more_node, second is rdf:first.
    items = [zero_or_more_node, RDF.first]
    Collection(self.shaclg, path_list_head, items)
    self.shaclg.add((property_shape, SH.path, path_list_head))
    if datatype is not None:
        shapes = self.create_datatype_shapes(datatype)
        tuples = self.shacl_or(shapes)
        self.shacl_add_to_shape(property_shape, tuples)
    if pattern is not None:
        self.shaclg.add((property_shape, SH.pattern, Literal(pattern)))
    array_length = None
    if array_dimensions is not None:
        ad = Collection(self.data_graph, array_dimensions)
        if len(ad) > 0:
            array_length = reduce(operator.mul, (item.toPython() for item in ad), 1)
    if array_length is not None and array_length > 0:
        # self.shaclg.add((property_shape, SH.minCount, Literal(array_length)))
        # minCount does not do what you think. SHACL 1.1 treats list as sets
        # so e.g. [1, 2, 1] has only 2 elements ...
        # We have to wait for SHACL 1.2 which provides an explicit list semantics
        # Until then, we will leave this comment in to remember that sh:minCount has been
        # commented out on purpose.
        self.shaclg.add((property_shape, SH.maxCount, Literal(array_length)))
    property_node_array = []
    property_node = BNode()
    self.shaclg.add((property_node, SH.property, property_shape))
    self.shaclg.add((property_node, SH.nodeKind, SH.BlankNode))
    property_node_array.append(property_node)
    if array_length is None or array_length == 0:
        property_node = BNode()
        self.shaclg.add((property_node, SH.hasValue, RDF.nil))
        property_node_array.append(property_node)
    return property_node_array
