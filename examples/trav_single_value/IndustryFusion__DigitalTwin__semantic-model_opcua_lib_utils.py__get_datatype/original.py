# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/lib/utils.py
# region: get_datatype (lines 270-277, stratum trav_single_value)
# licence of the source repository: see meta.json
def get_datatype(graph, node, typenode, templatenode, basens):
    datatype = next(graph.objects(node, basens['hasDatatype']), None)
    if datatype is None:
        if templatenode is not None:
            datatype = next(graph.objects(templatenode, basens['hasDatatype']), None)
        if datatype is None and typenode is not None:
            datatype = next(graph.objects(typenode, basens['hasDatatype']), None)
    return datatype
