"""Validation driver for Terramorpha__minergym__minergym_ontology.py__Ontology_surface_vertices.

The region is a method that only uses `self.rdf`, so `self` is a stub with
that one attribute: a graph built (identically on both sides, by the shim's
copy of minergym's own `intern_object`) from an epJSON-shaped object.

The graph holds
  * Wall_1: a three-vertex list (the property path rdf:rest*/rdf:first walks
    the whole RDF list) with an int and floats as coordinates;
  * Wall_2: a different surface with two vertices of its own, which must not
    leak into Wall_1's answer (and the reverse);
  * Wall_3: a vertex list one of whose vertices has no z coordinate -- that
    vertex joins nothing, the others still do;
  * Floor_9: a surface with no `vertices` at all (zero solutions), and a
    name that is no surface at all (zero solutions too).
A call with a surface that is not in the graph at all gives [] as well.
"""
from rdflib import Literal

from minergym_context import graph_from_object
from rdfeval.harness import run_pair

EPJSON = {
    "BuildingSurface:Detailed": {
        "Wall_1": {
            "surface_type": "Wall",
            "vertices": [
                {"vertex_x_coordinate": 0.0, "vertex_y_coordinate": 0.0, "vertex_z_coordinate": 3.0},
                {"vertex_x_coordinate": 5.0, "vertex_y_coordinate": 0.0, "vertex_z_coordinate": 3.0},
                {"vertex_x_coordinate": 5, "vertex_y_coordinate": 0.0, "vertex_z_coordinate": 0.0},
            ],
        },
        "Wall_2": {
            "surface_type": "Wall",
            "vertices": [
                {"vertex_x_coordinate": 10.0, "vertex_y_coordinate": 1.5, "vertex_z_coordinate": 2.5},
                {"vertex_x_coordinate": 11.0, "vertex_y_coordinate": 1.5, "vertex_z_coordinate": 2.5},
            ],
        },
        "Wall_3": {
            "surface_type": "Wall",
            "vertices": [
                {"vertex_x_coordinate": 7.0, "vertex_y_coordinate": 7.0, "vertex_z_coordinate": 7.0},
                {"vertex_x_coordinate": 8.0, "vertex_y_coordinate": 8.0},
            ],
        },
        "Floor_9": {"surface_type": "Floor"},
    },
}


class _Ontology:
    def __init__(self):
        self.rdf = graph_from_object(EPJSON)


def call(name):
    def _make():
        return (_Ontology(), Literal(name)), {}
    return _make


VERDICT = run_pair(
    __file__,
    entry='surface_vertices',
    calls=[call("Wall_1"), call("Wall_2"), call("Wall_3"), call("Floor_9"),
           call("BuildingSurface:Detailed"), call("Nowhere")],
    ordered=False,
)
