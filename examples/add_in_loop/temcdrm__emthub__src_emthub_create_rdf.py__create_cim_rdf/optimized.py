# Extracted from temcdrm/emthub@c9834a2c67 : src/emthub/create_rdf.py
# region: create_cim_rdf (lines 1031-1054, stratum add_in_loop)
# licence of the source repository: see meta.json
import rdflib
from context_shim import g, CIM, dyn_models, uuids, model_types_used
CIM_NS = 'http://www.ucaiug.org/grid18v15#'
EMT_NS = 'http://opensource.ieee.org/emtiop01v01#'

EMT = rdflib.Namespace(EMT_NS)
for key in model_types_used:
  model_type = dyn_models['DYR'][key]
  ID = model_type['mRID']
  uuids['NthAmDynamicModel:' + key] = ID
  mtyp = rdflib.URIRef (ID)
  g += [(mtyp, rdflib.RDF.type, EMT['NthAmDynamicModel']),
        (mtyp, CIM['IdentifiedObject.name'], rdflib.Literal(key, datatype=CIM.String)),
        (mtyp, CIM['IdentifiedObject.mRID'], rdflib.Literal(ID, datatype=CIM.String)),
        (mtyp, EMT['NthAmDynamicModel.modelKind'], EMT[f"NthAmModelKind.{model_type['modelKind']:s}"]),
        (mtyp, EMT['NthAmDynamicModel.nameKind'], EMT[f"NthAmModelNameKind.{model_type['nameKind']:s}"]),
        (mtyp, EMT['NthAmDynamicModel.statusKind'], EMT[f"NthAmModelStatusKind.{model_type['statusKind']:s}"]),
        (mtyp, EMT['NthAmDynamicModel.closestStandardModel'], rdflib.Literal(model_type['closestStandardModel'], datatype=CIM.String))]
  for parm in model_type['parameterDescriptors'][3:]:
    ID = parm['mRID']
    uuids[f"ParameterDescriptor:{key:s}_{parm['name']:s}"] = ID
    desc = rdflib.URIRef (ID)
    g += [(desc, rdflib.RDF.type, CIM.ParameterDescriptor),
          (desc, CIM['IdentifiedObject.name'], rdflib.Literal(parm['name'], datatype=CIM.String)),
          (desc, CIM['IdentifiedObject.mRID'], rdflib.Literal(ID, datatype=CIM.String)),
          (desc, CIM['DetailedModelDescriptor.DetailedModelTypeDynamics'], mtyp),
          (desc, CIM['ParameterDescriptor.typicalValue'], rdflib.Literal(parm['typicalValue'], datatype=CIM.String)),
          (desc, CIM['ParameterDescriptor.engineeringUnit'], rdflib.Literal(parm['engineeringUnit'], datatype=CIM.String)),
          (desc, CIM['ParameterDescriptor.sequenceNumber'], rdflib.Literal(parm['sequenceNumber'], datatype=CIM.Integer))]
