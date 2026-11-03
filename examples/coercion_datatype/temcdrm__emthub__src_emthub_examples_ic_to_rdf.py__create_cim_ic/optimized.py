# Extracted from temcdrm/emthub@c9834a2c67 : src/emthub/examples/ic_to_rdf.py
# region: create_cim_ic (lines 14-105, stratum coercion_datatype)
# licence of the source repository: see meta.json
import rdflib
import os
import pandas as pd
from otsrdflib import OrderedTurtleSerializer
CIM_NS = 'http://www.ucaiug.org/grid18v15#'
EMT_NS = 'http://opensource.ieee.org/emtiop01v01#'

def create_cim_ic (case):
  def read_ic (suffix, what):
    name = case['name']+suffix
    if os.path.exists(name):
      ic = pd.read_csv (name)
      print (what, 'from', name, 'read', ic.shape)
      #print (ic)
      return ic
  bus_ic = read_ic ('mb.txt', 'Initial bus numbers, base kV, Vpus, angles, and CN ids')
  gen_ic = read_ic ('mg.txt', 'Generator bus, p, q, types, and EQ ids')
  br_ic = read_ic ('mbr.txt', 'Branch from, to, tap, pf, qf, pt, qt and EQ/XfEnd ids')

  g = rdflib.Graph() # (store='Oxigraph')
  CIM = rdflib.Namespace (CIM_NS)
  g.bind('cim', CIM)
  g.bind('emt', EMT_NS)

  def power_flow (svid, tid, p, q):
    sv = rdflib.URIRef (svid)
    return [
      (sv, rdflib.RDF.type, CIM.SvPowerFlow),
      (sv, CIM['SvPowerFlow.Terminal'], rdflib.URIRef(tid)),
      (sv, CIM['SvPowerFlow.p'], rdflib.Literal (p, datatype=CIM.ActivePower)),
      (sv, CIM['SvPowerFlow.q'], rdflib.Literal (q, datatype=CIM.ReactivePower)),
    ]

  for i in range(len(bus_ic)):
    vmag = 1000.0 * bus_ic.iloc[i,1] * bus_ic.iloc[i,2]
    cnid = bus_ic.iloc[i,4]
    # temporary TopologicalNode for compliance with base CIM
    tn = rdflib.URIRef (cnid+'_TN')
    cn = rdflib.URIRef (cnid)
    sv = rdflib.URIRef (cnid+'_SvV')
    g += [
      (tn, rdflib.RDF.type, CIM.TopologicalNode),
      (cn, rdflib.RDF.type, CIM.ConnectivityNode),
      (cn, CIM['ConnectivityNode.TopologicalNode'], tn),
      (sv, rdflib.RDF.type, CIM.SvVoltage),
      (sv, CIM['SvVoltage.TopologicalNode'], tn),
      (sv, CIM['SvVoltage.v'], rdflib.Literal (vmag, datatype=CIM.Voltage)),
      (sv, CIM['SvVoltage.angle'], rdflib.Literal (bus_ic.iloc[i,3], datatype=CIM.AngleDegrees)),
    ]

  for i in range(len(br_ic)):
    tap = br_ic.iloc[i,2]
    p1 = 1.0e6 * br_ic.iloc[i,3]
    q1 = 1.0e6 * br_ic.iloc[i,4]
    p2 = 1.0e6 * br_ic.iloc[i,5]
    q2 = 1.0e6 * br_ic.iloc[i,6]
    t1id = br_ic.iloc[i,7]
    t2id = br_ic.iloc[i,8]
    svid = t1id.split('_')[0] + ('_SvXfmrPF_' if tap > 0.0 else '_SvLinePF_')
    g += power_flow (svid+'1', t1id, p1, q1) + power_flow (svid+'2', t2id, p2, q2)

  # positive generation sign changes to follow load convention, into the From bus
  for i in range(len(gen_ic)):
    p1 = -1.0e6 * gen_ic.iloc[i,1]
    q1 = -1.0e6 * gen_ic.iloc[i,2]
    t1id = gen_ic.iloc[i,4]
    g += power_flow (t1id.split('_')[0]+'_SvGenPF', t1id, p1, q1)

  serializer = OrderedTurtleSerializer(g)
  serializer.class_order = [
    CIM.SvPowerFlow,
    CIM.SvVoltage,
    CIM.TopologicalNode
  ]
  ic_name = case['name']+'_ic.ttl'
  with open(ic_name, 'wb') as fp:
    serializer.serialize(fp)
  print ('wrote initial conditions to', ic_name)
