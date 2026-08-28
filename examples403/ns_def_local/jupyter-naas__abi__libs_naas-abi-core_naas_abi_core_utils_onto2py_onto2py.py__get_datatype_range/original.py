# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-core/naas_abi_core/utils/onto2py/onto2py.py
# region: get_datatype_range (lines 1675-1694, stratum ns_def_local)
# licence of the source repository: see meta.json
import rdflib

def get_datatype_range(g: rdflib.Graph, prop) -> str | None:
    """Get the datatype range for a data property"""
    RDFS = rdflib.Namespace("http://www.w3.org/2000/01/rdf-schema#")
    XSD = rdflib.Namespace("http://www.w3.org/2001/XMLSchema#")

    datatype_mapping = {
        str(XSD.string): "str",
        str(XSD.integer): "int",
        str(XSD.int): "int",
        str(XSD.float): "float",
        str(XSD.double): "float",
        str(XSD.boolean): "bool",
        str(XSD.date): "datetime.date",
        str(XSD.dateTime): "datetime.datetime",
    }

    for range_type in g.objects(prop, RDFS.range):
        return datatype_mapping.get(str(range_type), "Any")

    return "Any"
