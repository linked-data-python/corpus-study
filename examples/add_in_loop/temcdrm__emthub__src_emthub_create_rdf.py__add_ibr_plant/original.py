# Extracted from temcdrm/emthub@c9834a2c67 : src/emthub/create_rdf.py
# region: add_ibr_plant (lines 1474-1501, stratum add_in_loop)
# licence of the source repository: see meta.json
import rdflib
from .dll_config import get_dll_cim_parameter_kind
EMT_NS = 'http://opensource.ieee.org/emtiop01v01#'

for parm in d['ParametersInfo']:
  kind = get_dll_cim_parameter_kind (parm['DataType'])
  val = str(parm['DefaultValue'])
  #print (seq, kind, val)
  ptID = dllID+'_{:d}'.format(seq)
  pt = rdflib.URIRef (ptID)
  g.add ((pt, rdflib.RDF.type, rdflib.URIRef (EMT_NS + 'IEEECigreDLLParameter')))
  g.add ((pt, rdflib.URIRef (EMT_NS + 'IEEECigreDLLParameter.IEEECigreDLL'), dll))
  g.add ((pt, rdflib.URIRef (EMT_NS + 'IEEECigreDLLParameter.dllSequenceNumber'), rdflib.Literal(seq, datatype=CIM.Integer)))
  g.add ((pt, rdflib.URIRef (EMT_NS + 'IEEECigreDLLParameter.value'), rdflib.Literal(val, datatype=CIM.String)))
  g.add ((pt, rdflib.URIRef (EMT_NS + 'IEEECigreDLLParameter.dllParameterKind'), rdflib.URIRef (EMT_NS + 'IEEECigreDLLParameterKind.{:s}'.format(kind))))
  # make an info class
  infID = ptID + '_info'
  inf = rdflib.URIRef(infID)
  g.add ((pt, rdflib.URIRef (EMT_NS + 'IEEECigreDLLParameter.IEEECigreDLLParameterInfo'), inf))
  g.add ((inf, rdflib.RDF.type, rdflib.URIRef (EMT_NS + 'IEEECigreDLLParameterInfo')))
  g.add ((inf, rdflib.URIRef (EMT_NS + 'IEEECigreDLLParameterInfo.dllName'), rdflib.Literal (parm['Name'], datatype=CIM.String)))
  g.add ((inf, rdflib.URIRef (EMT_NS + 'IEEECigreDLLParameterInfo.dllGroupName'), rdflib.Literal (parm['GroupName'], datatype=CIM.String)))
  g.add ((inf, rdflib.URIRef (EMT_NS + 'IEEECigreDLLParameterInfo.dllDescription'), rdflib.Literal (parm['Description'], datatype=CIM.String)))
  g.add ((inf, rdflib.URIRef (EMT_NS + 'IEEECigreDLLParameterInfo.dllUnit'), rdflib.Literal (parm['Unit'], datatype=CIM.String)))
  g.add ((inf, rdflib.URIRef (EMT_NS + 'IEEECigreDLLParameterInfo.dllDefaultValue'), rdflib.Literal (str(parm['DefaultValue']), datatype=CIM.String)))
  g.add ((inf, rdflib.URIRef (EMT_NS + 'IEEECigreDLLParameterInfo.dllMinValue'), rdflib.Literal (str(parm['MinValue']), datatype=CIM.String)))
  g.add ((inf, rdflib.URIRef (EMT_NS + 'IEEECigreDLLParameterInfo.dllMaxValue'), rdflib.Literal (str(parm['MaxValue']), datatype=CIM.String)))
  bFixed = False
  if parm['FixedValue'] != 0:
    bFixed = True
  g.add ((inf, rdflib.URIRef (EMT_NS + 'IEEECigreDLLParameterInfo.dllFixedValue'), rdflib.Literal (bFixed, datatype=CIM.Boolean)))
  seq += 1
