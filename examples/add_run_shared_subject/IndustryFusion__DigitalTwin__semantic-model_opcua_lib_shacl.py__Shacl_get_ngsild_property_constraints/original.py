# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/lib/shacl.py
# region: Shacl.get_ngsild_property_constraints (lines 323-393, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, SH, split_uri

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
