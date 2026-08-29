# Extracted from temcdrm/emthub@c9834a2c67 : src/emthub/create_rdf.py
# region: ConnectToDCNode (lines 185-195, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
import rdflib
CIM_NS = 'http://www.ucaiug.org/grid18v15#'
EMT_NS = 'http://opensource.ieee.org/emtiop01v01#'

def ConnectToDCNode (g, eq_id, dcn_id, sequenceNumber, CIM, bHybrid = False):
  trm_id = '{:s}_dc{:d}'.format (eq_id, sequenceNumber)
  trm = rdflib.URIRef (trm_id)
  if bHybrid:
    g.add ((trm, rdflib.RDF.type, rdflib.URIRef (EMT_NS + 'PowerElectronicsConnectionDCTerminal')))
    g.add ((trm, rdflib.URIRef (EMT_NS + 'PowerElectronicsConnectionDCTerminal.PowerElectronicsConnection'), eq_id))
  else:
    g.add ((trm, rdflib.RDF.type, rdflib.URIRef (CIM_NS + 'DCTerminal')))
    g.add ((trm, rdflib.URIRef (CIM_NS + 'DCTerminal.DCConductingEquipment'), eq_id))
  g.add ((trm, rdflib.URIRef (CIM_NS + 'DCBaseTerminal.DCNode'), dcn_id))
  g.add ((trm, rdflib.URIRef (CIM_NS + 'ACDCTerminal.sequenceNumber'), rdflib.Literal (sequenceNumber, datatype=CIM.Integer)))
