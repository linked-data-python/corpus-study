# Extracted from temcdrm/emthub@c9834a2c67 : src/emthub/create_rdf.py
# region: add_ibr_plant (lines 1474-1501, stratum add_in_loop)
# licence of the source repository: see meta.json
import rdflib
from context_shim import g, d, dll, dllID, seq, CIM, get_dll_cim_parameter_kind
EMT_NS = 'http://opensource.ieee.org/emtiop01v01#'

EMT = rdflib.Namespace(EMT_NS)
for parm in d['ParametersInfo']:
  kind = get_dll_cim_parameter_kind (parm['DataType'])
  val = str(parm['DefaultValue'])
  #print (seq, kind, val)
  pt = rdflib.URIRef(f'{dllID}_{seq}')
  # make an info class
  inf = rdflib.URIRef(f'{pt}_info')
  g += [(pt, rdflib.RDF.type, EMT['IEEECigreDLLParameter']),
        (pt, EMT['IEEECigreDLLParameter.IEEECigreDLL'], dll),
        (pt, EMT['IEEECigreDLLParameter.dllSequenceNumber'], rdflib.Literal(seq, datatype=CIM.Integer)),
        (pt, EMT['IEEECigreDLLParameter.value'], rdflib.Literal(val, datatype=CIM.String)),
        (pt, EMT['IEEECigreDLLParameter.dllParameterKind'], EMT[f'IEEECigreDLLParameterKind.{kind:s}']),
        (pt, EMT['IEEECigreDLLParameter.IEEECigreDLLParameterInfo'], inf),
        (inf, rdflib.RDF.type, EMT['IEEECigreDLLParameterInfo']),
        (inf, EMT['IEEECigreDLLParameterInfo.dllName'], rdflib.Literal(parm['Name'], datatype=CIM.String)),
        (inf, EMT['IEEECigreDLLParameterInfo.dllGroupName'], rdflib.Literal(parm['GroupName'], datatype=CIM.String)),
        (inf, EMT['IEEECigreDLLParameterInfo.dllDescription'], rdflib.Literal(parm['Description'], datatype=CIM.String)),
        (inf, EMT['IEEECigreDLLParameterInfo.dllUnit'], rdflib.Literal(parm['Unit'], datatype=CIM.String)),
        (inf, EMT['IEEECigreDLLParameterInfo.dllDefaultValue'], rdflib.Literal(val, datatype=CIM.String)),
        (inf, EMT['IEEECigreDLLParameterInfo.dllMinValue'], rdflib.Literal(str(parm['MinValue']), datatype=CIM.String)),
        (inf, EMT['IEEECigreDLLParameterInfo.dllMaxValue'], rdflib.Literal(str(parm['MaxValue']), datatype=CIM.String)),
        (inf, EMT['IEEECigreDLLParameterInfo.dllFixedValue'], rdflib.Literal(parm['FixedValue'] != 0, datatype=CIM.Boolean))]
  seq += 1
