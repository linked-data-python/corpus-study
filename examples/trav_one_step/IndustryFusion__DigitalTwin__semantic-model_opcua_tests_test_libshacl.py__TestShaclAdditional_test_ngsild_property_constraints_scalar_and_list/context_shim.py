# Context shim (see meta.json): the region reads back a SHACL graph built by
# `self.sh.get_ngsild_property_constraints(...)`, a method of the `Shacl`
# class -- IndustryFusion/DigitalTwin@3b40088b880811f61df63ba926f78256098ce695 :
# semantic-model/opcua/lib/shacl.py -- which the pipeline's context window did
# not capture (it is a sibling class, imported by test_libshacl.py, not
# inlined in the test method). Reproduced here, verbatim, trimmed to exactly
# the methods this region's two calls reach: `__init__`,
# `get_ngsild_property_constraints`, `get_array_validation_shape`,
# `create_datatype_shapes`, `shacl_add_to_shape`, `shacl_or`.
# `get_array_validation_shape_for_iri` is not transcribed: both calls in the
# region pass `is_iri=False`, so the branch that would reach it never runs.
# NGSILD is lib/utils.py's module-level constant. Identical bindings for both
# representations.
from rdflib import Graph, Namespace, Literal, BNode
from rdflib.namespace import RDF, SH
from rdflib.collection import Collection
from functools import reduce
import operator

NGSILD = Namespace('https://uri.etsi.org/ngsi-ld/')


class Shacl:
    def __init__(self, data_graph, namespace_prefix, basens, opcuans, value_rank_subshapes_enabled=False):
        self.shaclg = Graph()
        self.shacl_namespace = Namespace(f'{namespace_prefix}shacl/')
        self.shaclg.bind('shacl', self.shacl_namespace)
        self.shaclg.bind('sh', SH)
        self.ngsildns = NGSILD
        self.shaclg.bind('ngsi-ld', self.ngsildns)
        self.basens = basens
        self.opcuans = opcuans
        self.data_graph = data_graph
        self.value_rank_subshapes_enabled = value_rank_subshapes_enabled

    def create_datatype_shapes(self, datatypes):
        if datatypes is None or len(datatypes) == 0:
            return []
        else:
            dt_items = []
            for dt in datatypes:
                dt_node = BNode()
                self.shaclg.add((dt_node, SH.datatype, dt))
                dt_items.append(dt_node)
            return dt_items

    def shacl_add_to_shape(self, property_shape, tuples):
        if tuples is not None:
            for tup in tuples:
                self.shaclg.add((property_shape, tup[0], tup[1]))

    def shacl_or(self, shapes):
        """Creates shacl_or node if more than one shape is provided

           In case only one shape is provided, then the "inner" properties are returned
           In case of more shapes, it is wrapped in an SHACL OR expression
        Args:
            shapes (): shapes to or, e.g. (in turtle notation) ( [sh:datatype xsd:integer] [sh:datatype xsd:string])

        Returns:
            RDF Nodes as tuple: (predicate, object)
        """
        if len(shapes) == 1:
            result = []
            # Get all elements in blank node
            for s, p, o in self.shaclg.triples((shapes[0], None, None)):
                result.append((p, o))
                # remove subject, it is expected to be relinked by the caller
                self.shaclg.remove((s, p, o))
            return result
        or_node = BNode()
        Collection(self.shaclg, or_node, shapes)
        return [(SH['or'], or_node)]

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

    def get_ngsild_property_constraints(self, value_rank, array_dimensions, datatype, pattern, is_iri, contentclass):
        """Create constraints for ngsi-ld Property

        There are three kind of specified properties:
        - "Property": Default scalar property, e.g. "value": 1
        - "ListProperty": List of Properties, e.g. "listValue": [1, 2, 3]
        - "JsonProerty": JSON Property, e.g. "json": {"key": "value"}

        Args:
            value_rank (int): OPC UA defined Value Rank
            array_dimensions (list(int)): list of integers according to OPC UA arrayDimension attribute
            datatype (URIRef): XSD Datatype
            pattern (str): Patter for generic Placeholder
        """
        shapes_list = []
        json_datatype = []
        non_json_datatypes = []
        if datatype is not None:
            json_datatype = [x for x in datatype if x == RDF.JSON]
            non_json_datatypes = [x for x in datatype if x != RDF.JSON]
        if value_rank is None or (int(value_rank) < 0 and len(non_json_datatypes) > 0):
            innerproperty = BNode()
            # It is a scalar!
            self.shaclg.add((innerproperty, SH.path, self.ngsildns['hasValue']))
            if is_iri:
                self.shaclg.add((innerproperty, SH.nodeKind, SH.IRI))
                if contentclass is not None:
                    self.shaclg.add((innerproperty, SH['class'], contentclass))
            else:
                self.shaclg.add((innerproperty, SH.nodeKind, SH.Literal))
                shapes = self.create_datatype_shapes(non_json_datatypes)
                tuples = self.shacl_or(shapes)
                self.shacl_add_to_shape(innerproperty, tuples)
            self.shaclg.add((innerproperty, SH.minCount, Literal(1)))
            self.shaclg.add((innerproperty, SH.maxCount, Literal(1)))
            shape_node = BNode()
            self.shaclg.add((shape_node, SH.property, innerproperty))
            shapes_list.append(shape_node)
        if value_rank is not None and int(value_rank) != -1:
            # It is a list!
            innerproperty = BNode()
            self.shaclg.add((innerproperty, SH.path, self.ngsildns['hasValueList']))
            if is_iri:
                array_validation_shape = self.get_array_validation_shape_for_iri(contentclass, array_dimensions)
            else:
                array_validation_shape = self.get_array_validation_shape(datatype,
                                                                         pattern,
                                                                         value_rank,
                                                                         array_dimensions)
            tuples = self.shacl_or(array_validation_shape)
            self.shacl_add_to_shape(innerproperty, tuples)
            self.shaclg.add((innerproperty, SH.minCount, Literal(1)))
            self.shaclg.add((innerproperty, SH.maxCount, Literal(1)))
            shape_node = BNode()
            self.shaclg.add((shape_node, SH.property, innerproperty))
            shapes_list.append(shape_node)
        if len(json_datatype) > 0 and (value_rank is None or int(value_rank) < 0):
            # Treat JSON separate due to NGSI-LD specification
            innerproperty = BNode()
            self.shaclg.add((innerproperty, SH.path, self.ngsildns['hasJSON']))
            self.shaclg.add((innerproperty, SH.nodeKind, SH.Literal))
            shapes = self.create_datatype_shapes(json_datatype)
            tuples = self.shacl_or(shapes)
            self.shacl_add_to_shape(innerproperty, tuples)

            self.shaclg.add((innerproperty, SH.minCount, Literal(1)))
            self.shaclg.add((innerproperty, SH.maxCount, Literal(1)))
            shape_node = BNode()
            self.shaclg.add((shape_node, SH.property, innerproperty))
            shapes_list.append(shape_node)
        return shapes_list
