# Extracted from binary-array-ld/bald@ca59666abe : nc2rdf/nc2rdf.py
# region: baldgraph2schemaorg (lines 29-95, stratum ns_def_local)
# licence of the source repository: see meta.json
import bald
import rdflib
import json
from rdflib import Namespace, BNode, URIRef, Literal

def baldgraph2schemaorg(graph, path=None, baseuri=None):
    """
       Input: netCDF file
       Transforms to a rdflib.Graph bald style
       Returns a new graph in schema.org profile
    """
    # HACK: The following mappings ignore prefixes as well as prefixes in nc file
    # TODO: Fix references to prefixes/aliases proper

    #encoding formats to use - one as Text, one as URL
    encodingFormats = ["application/x-netcdf",
                       "http://vocab.nerc.ac.uk/collection/M01/current/NC/"]

    #load mappings
    mapping_idx = {}
    mapping_data = []
    with open('bald2schemaorg_mappings.json' , 'r') as f:
       mapping_data = json.load(f)

    for item in mapping_data:
       mapping_idx[item['bald']] = item['schemaorg']

    qres = graph.query(
    """PREFIX bald: <http://binary-array-ld.net/latest/> 
       SELECT DISTINCT ?pred ?value
       WHERE {
          ?c a bald:Container .
          ?c ?pred ?value
       }""")

    schema_g = rdflib.Graph()

    if baseuri is not None:
       container = URIRef(baseuri)
    else:
       container = BNode()

    so = Namespace("http://schema.org/")
    schema_g.add( (container, URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), so.Dataset) )

    if path is not None and isUrl(path):
       predUri = URIRef("http://schema.org/url")
       schema_g.add( (container, predUri, URIRef(path)) )

    for row in qres:
       currField = getBasename(str(row[0])).strip()
       #print(getBasename(str(row[0])) + ' (type: ' + str(type(row[0])) + ")" + " :: " + row[1] + ' (type: ' + str(type(row[1])) + ")")
       if(currField in mapping_idx.keys()):
          predUri = URIRef("http://schema.org/" + mapping_idx[currField])
          if currField == 'keywords':
             for x in row[1].split(','):
                kw = x.strip()
                if len(kw) == 0:
                   continue
                lit = Literal(kw)
                schema_g.add( (container, predUri, lit) )
             continue

          #print('schemaorg:' + mapping_idx[currField], "\t", row[1])
          lit = Literal(row[1])
          schema_g.add( (container, predUri, lit) )
    #
    # Add some distrbution details
    #
    schema_org_inst  =  bald.schemaOrg()
    schema_g  =  schema_org_inst.distribution(container, schema_g, baseuri)
    return schema_g
