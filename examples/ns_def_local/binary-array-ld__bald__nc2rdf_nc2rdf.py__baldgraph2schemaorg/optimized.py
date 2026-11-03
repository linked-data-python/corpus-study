# Extracted from binary-array-ld/bald@ca59666abe : nc2rdf/nc2rdf.py
# region: baldgraph2schemaorg (lines 29-95, stratum ns_def_local)
# licence of the source repository: see meta.json
import rdflib
import json
from rdflib import Namespace, BNode, URIRef, Literal
import _shim as bald
from _shim import isUrl, getBasename

def baldgraph2schemaorg(graph, path=None, baseuri=None):
    """
       Input: netCDF file
       Transforms to a rdflib.Graph bald style
       Returns a new graph in schema.org profile
    """
    # HACK: The following mappings ignore prefixes as well as prefixes in nc file
    # TODO: Fix references to prefixes/aliases proper

    #load mappings
    with open('bald2schemaorg_mappings.json' , 'r') as f:
       mapping_idx = {item['bald']: item['schemaorg'] for item in json.load(f)}

    qres = graph.query(
    """PREFIX bald: <http://binary-array-ld.net/latest/> 
       SELECT DISTINCT ?pred ?value
       WHERE {
          ?c a bald:Container .
          ?c ?pred ?value
       }""")

    schema_g = rdflib.Graph()
    container = URIRef(baseuri) if baseuri is not None else BNode()

    so = Namespace("http://schema.org/")
    schema_g.add( (container, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), so.Dataset) )

    if path is not None and isUrl(path):
       schema_g.add( (container, so.url, URIRef(path)) )

    for pred, value in qres:
       currField = getBasename(str(pred)).strip()
       #print(getBasename(str(row[0])) + ' (type: ' + str(type(row[0])) + ")" + " :: " + row[1] + ' (type: ' + str(type(row[1])) + ")")
       if currField in mapping_idx:
          predUri = so[mapping_idx[currField]]
          if currField == 'keywords':
             schema_g += [(container, predUri, Literal(kw))
                          for kw in map(str.strip, value.split(',')) if kw]
          else:
             #print('schemaorg:' + mapping_idx[currField], "\t", row[1])
             schema_g.add( (container, predUri, Literal(value)) )
    #
    # Add some distrbution details
    #
    return bald.schemaOrg().distribution(container, schema_g, baseuri)
