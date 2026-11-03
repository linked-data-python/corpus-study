# Extracted from pyscal/atomRDF@c9b070e15f : atomrdf/datamodels/workflow/operations.py
# region: Shear.from_graph (lines 359-399, stratum trav_navigation)
# licence of the source repository: see meta.json
from atomrdf_context import get_sample_object, classmethod, CMSO, PROV

@classmethod
def from_graph(cls, graph, activity_id):
    def components(vector):
        return [graph.value(vector, CMSO[f"hasComponent_{axis}"]).toPython() for axis in "xyz"]

    activity = get_sample_object(activity_id)
    output_sample = next(graph.subjects(PROV.wasGeneratedBy, activity), None)
    input_sample = graph.value(output_sample, PROV.wasDerivedFrom) if output_sample else None
    vec = next(graph.objects(activity, CMSO.hasVector), None)
    shear_vector = components(vec) if vec is not None else None

    normal_vector = distance = None
    plane = graph.value(activity, CMSO.hasPlane)
    if plane is not None:
        nv = graph.value(plane, CMSO.hasNormalVector)
        if nv is not None:
            normal_vector = components(nv)
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
