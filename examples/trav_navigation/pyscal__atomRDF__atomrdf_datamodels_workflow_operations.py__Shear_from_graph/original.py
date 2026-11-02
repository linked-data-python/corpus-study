# Extracted from pyscal/atomRDF@c9b070e15f : atomrdf/datamodels/workflow/operations.py
# region: Shear.from_graph (lines 359-399, stratum trav_navigation)
# licence of the source repository: see meta.json
from atomrdf.utils import get_sample_object
from atomrdf.namespace import (
    CMSO,
    LDO,
    PLDO,
    PODO,
    CDCO,
    PROV,
    Literal,
    ASMO,
)

@classmethod
def from_graph(cls, graph, activity_id):
    activity = get_sample_object(activity_id)
    output_sample = next(
        (s for s, _, _ in graph.triples((None, PROV.wasGeneratedBy, activity))),
        None,
    )
    input_sample = (
        graph.value(output_sample, PROV.wasDerivedFrom) if output_sample else None
    )

    shear_vector = None
    for vec in graph.objects(activity, CMSO.hasVector):
        x = graph.value(vec, CMSO.hasComponent_x)
        y = graph.value(vec, CMSO.hasComponent_y)
        z = graph.value(vec, CMSO.hasComponent_z)
        shear_vector = [x.toPython(), y.toPython(), z.toPython()]
        break

    normal_vector = None
    distance = None
    plane = graph.value(activity, CMSO.hasPlane)
    if plane is not None:
        nv = graph.value(plane, CMSO.hasNormalVector)
        if nv is not None:
            x = graph.value(nv, CMSO.hasComponent_x)
            y = graph.value(nv, CMSO.hasComponent_y)
            z = graph.value(nv, CMSO.hasComponent_z)
            normal_vector = [x.toPython(), y.toPython(), z.toPython()]
        d = graph.value(plane, CMSO.hasDistanceFromOrigin)
        if d is not None:
            distance = d.toPython()

    return cls(
        id=str(activity_id),
        input_sample=str(input_sample) if input_sample else None,
        output_sample=str(output_sample) if output_sample else None,
        shear_vector=shear_vector,
        normal_vector=normal_vector,
        distance=distance,
    )
