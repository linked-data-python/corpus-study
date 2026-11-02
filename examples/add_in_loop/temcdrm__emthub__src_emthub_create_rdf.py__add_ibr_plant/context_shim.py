# Context shim (see meta.json): the names that surround
# add_ibr_plant's loop in temcdrm/emthub@c9834a2c67 : src/emthub/create_rdf.py
# (the loop sits inside a function that has built `g`, `dll`, `dllID` and `d`
# just above it) and src/emthub/dll_config.py, so the statement executes
# outside the package (emthub imports networkx, otsrdflib, ... at import
# time).
# Identical bindings for both representations.
#
# - get_dll_cim_parameter_kind: VERBATIM from emthub/dll_config.py.
# - CIM = rdflib.Namespace (CIM_NS), CIM_NS = 'http://www.ucaiug.org/grid18v15#'
#   (create_rdf.py lines 34 and 247).
# - g, dll, dllID, seq, d: the graph, the DLL node, its identifier, the
#   running parameter sequence number (`seq = 0` just before the loop) and
#   the DLL description dictionary, whose 'ParametersInfo' list is the shape
#   emthub reads from a Cigre DLL's JSON interface description. The values
#   below are invented sample parameters (nothing in the region depends on
#   what they are, only on their types).
import rdflib

CIM_NS = 'http://www.ucaiug.org/grid18v15#'
CIM = rdflib.Namespace(CIM_NS)


def get_dll_cim_parameter_kind (idx):
  if idx == 1:
    return 'Char_Val'
  if idx == 2:
    return 'Int8_Val'
  if idx == 3:
    return 'Uint8_Val'
  if idx == 4:
    return 'Int16_Val'
  if idx == 5:
    return 'Uint16_Val'
  if idx == 6:
    return 'Int32_Val'
  if idx == 7:
    return 'Uint32_Val'
  if idx == 8:
    return 'Real32_Val'
  if idx == 9:
    return 'Real64_Val'
  if idx == 10:
    return 'Char_Ptr'


g = rdflib.Graph()
dllID = 'urn:uuid:5a6f2c0e-1c3b-4a39-9f6e-0d3f6b1f7a10'
dll = rdflib.URIRef(dllID)
# the DLL node already carries a triple when the loop starts
g.add((dll, rdflib.URIRef('http://www.ucaiug.org/grid18v15#IdentifiedObject.name'),
       rdflib.Literal('ibr_plant', datatype=CIM.String)))
seq = 0
d = {
  'ModelName': 'ibr_plant',
  'ParametersInfo': [
    {'Name': 'Vbase', 'GroupName': 'Base values', 'Description': 'Base voltage, "line to line"',
     'Unit': 'kV', 'DataType': 9, 'FixedValue': 0,
     'DefaultValue': 13.8, 'MinValue': 0.0, 'MaxValue': 500.0},
    {'Name': 'Mode', 'GroupName': 'Control', 'Description': 'Control mode\n0 = grid following',
     'Unit': 'N/A', 'DataType': 6, 'FixedValue': 1,
     'DefaultValue': 0, 'MinValue': 0, 'MaxValue': 3},
    {'Name': 'Label', 'GroupName': 'Control', 'Description': '',
     'Unit': '', 'DataType': 10, 'FixedValue': 2,
     'DefaultValue': 'unit-é', 'MinValue': '', 'MaxValue': ''},
    {'Name': 'Ramp', 'GroupName': 'Limits', 'Description': 'Ramp rate',
     'Unit': 'pu/s', 'DataType': 8, 'FixedValue': 0.0,
     'DefaultValue': 1e-3, 'MinValue': -1e6, 'MaxValue': 1e6},
    {'Name': 'Enable', 'GroupName': 'Control', 'Description': 'Enable flag',
     'Unit': 'N/A', 'DataType': 2, 'FixedValue': -1,
     'DefaultValue': True, 'MinValue': False, 'MaxValue': True},
  ],
}
