# Extracted from landrs-toolkit/PySOSA@1993668bd7 : PySOSA/Actuator.py
# region: Actuator.__init__ (lines 22-46, band high)
# licence of the source repository: see meta.json
from rdflib import BNode, Literal, RDF, RDFS
from PySOSA import config as cfg
from PySOSA.ActuatableProperty import ActuatableProperty
from PySOSA.Procedure import Procedure
obsgraph = cfg.get_graph()

def __init__(self, *args):
    """ instantiating Actuator object
       Args:
           *args (str): label, comment, actuatable property, prdocedure
       Returns:
           actuator object: instantiated with actuator  properties
    """
    self.actuator_id = BNode()
    self.platform_id = BNode()
    self.label = Literal(args[0])
    self.comment = Literal(args[1])
    self.actuatableProperty = (args[2])
    self.procedure = Literal(args[3])

    obsgraph.add((self.actuator_id, RDF.type, cfg.sosa.Actuator))
    obsgraph.add((self.actuator_id, RDFS.comment, self.comment))
    obsgraph.add((self.actuator_id, RDFS.label, self.label))
    # add list of actuatable properties
    for act in self.actuatableProperty:
        if isinstance(act, ActuatableProperty):
            obsgraph.add((self.actuator_id, cfg.sosa.observes, act.label))
    # add list of procedures
    for pro in self.procedure:
        if isinstance(pro, Procedure):
            obsgraph.add((self.sensor_id, cfg.sosa.implements, pro.label))


# --- demo harness (added identically to both representations; see meta.json) ---
# The region writes into the module-level `obsgraph` and returns nothing, so
# that graph is the observable.  In this extract __init__ is a plain
# module-level function; call it on a bare instance.
class _Instance:
    pass


__init__(_Instance(),
         "Valve 1",
         "The main water valve of the demo deployment",
         [ActuatableProperty("water flow", "the flow the valve actuates"),
          "not an ActuatableProperty"],
         "open the valve")
