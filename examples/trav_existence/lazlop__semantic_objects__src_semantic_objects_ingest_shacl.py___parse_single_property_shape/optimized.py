# Extracted from lazlop/semantic_objects@243c5efd8c : src/semantic_objects/ingest/shacl.py
# region: _parse_single_property_shape (lines 242-350, stratum trav_existence)
# licence of the source repository: see meta.json
from typing import List, Optional, Tuple, Union
from rdflib import BNode, Graph, RDF, URIRef
from rdflib.namespace import RDFS
# `semantic_objects` is not installed. The relative imports of the package
# (namespaces.SH, ir.*, naming.*) and the helpers defined above the region in
# the same file (shacl.py lines 1-241) come from a context shim, verbatim
# copies from the repository at the pinned commit (see meta.json).
from semantic_objects_context import (
    SH, ComplexConstraintIR, PinIR, PropertyShapeIR,
    field_name_for_path, field_name_for_qualified, local_name,
    _literal_str, _literal_int, _dump_subgraph, _iter_alternations,
    _parse_nested_pins, _parse_or_members, _or_property_shape,
    _parse_alternation_property_shape,
)
_ALTERNATION_PREDICATES = (SH['or'], SH.xone)

def _parse_single_property_shape(g: Graph, bn) -> Union[PropertyShapeIR, ComplexConstraintIR]:
    """Parse one sh:property bnode into a PropertyShapeIR (it reduces to a
    field) or a ComplexConstraintIR (it doesn't). Shared by the class's direct
    sh:property walk and by class-level sh:or/xone branches that each wrap a
    full sh:property bnode of their own (see _parse_class_level_alternation)."""
    path_obj = g.value(bn, SH.path)
    comment = _literal_str(g, bn, RDFS.comment)
    message = _literal_str(g, bn, SH.message)
    severity = _literal_str(g, bn, SH.severity)

    def complex_constraint(path_local, kind):
        return ComplexConstraintIR(
            path_local=path_local, kind=kind, comment=comment, message=message,
            severity=severity, raw_turtle=_dump_subgraph(g, bn),
        )

    if path_obj is None or isinstance(path_obj, BNode):
        return complex_constraint(None, 'inverse-path')

    path_local = local_name(path_obj)
    max_count = _literal_int(g, bn, SH.maxCount)
    min_count = _literal_int(g, bn, SH.minCount)
    if (bn, SH.sparql, None) in g:
        return complex_constraint(path_local, 'sparql')
    if any((bn, pred, None) in g for pred in _ALTERNATION_PREDICATES):
        shape = _parse_alternation_property_shape(g, bn, path_local, comment, message)
        return shape or complex_constraint(path_local, 'or')
    if max_count == 0:
        return complex_constraint(path_local, 'forbidden')

    direct_class = g.value(bn, SH['class'])
    datatype = g.value(bn, SH.datatype)
    if direct_class is not None or datatype is not None:
        return PropertyShapeIR(
            path_local=path_local,
            field_name=field_name_for_path(path_local),
            target_class_local=local_name(direct_class) if direct_class is not None else None,
            datatype_local=local_name(datatype) if datatype is not None else None,
            min_count=min_count, max_count=max_count, qualified=False,
            comment=comment, message=message,
        )

    qvs = g.value(bn, SH.qualifiedValueShape)
    if qvs is not None:
        qvs_class = g.value(qvs, SH['class'])
        if qvs_class is None:
            # No sh:class of its own - still resolves cleanly if the
            # qualified value shape's *entire* content is an sh:or/sh:xone of
            # alternative classes (e.g. FanCoilUnit: `sh:qualifiedValueShape
            # [ sh:xone ( [sh:class Role-Cooling] [sh:class Role-Heating] ) ]`,
            # no sh:node wrapper at all) - same Union-field pattern as a bare
            # property-shape-level alternation, just qualified.
            qvs_alt_list, qvs_alt_pred = next(_iter_alternations(g, qvs), (None, None))
            if qvs_alt_list is not None and set(g.predicates(qvs)) == {qvs_alt_pred}:
                branches = _parse_or_members(g, qvs_alt_list, path_local)
                if branches is not None:
                    qmin = _literal_int(g, bn, SH.qualifiedMinCount)
                    return _or_property_shape(
                        path_local, branches,
                        min_count=qmin, max_count=None, qualified=True,
                        comment=comment, message=message,
                    )
            return complex_constraint(path_local, 'nested-node')
        qmin = _literal_int(g, bn, SH.qualifiedMinCount)
        target_local = local_name(qvs_class)
        shape = PropertyShapeIR(
            path_local=path_local,
            field_name=field_name_for_qualified(target_local),
            target_class_local=target_local, datatype_local=None,
            min_count=qmin, max_count=None, qualified=True,
            comment=comment, message=message,
        )
        extra_preds = set(g.predicates(qvs)) - {SH['class']}
        if SH.node in extra_preds:
            pins = _parse_nested_pins(g, qvs)
            if pins:
                shape.nested_pins = pins
                extra_preds.discard(SH.node)
        if extra_preds:
            shape.supplementary_notes.append(ComplexConstraintIR(
                path_local=path_local, kind='nested-node',
                comment="Additional constraints on the qualified value beyond its class "
                        "(medium, sub-shape, etc.) - see raw_turtle.",
                message=message, severity=severity, raw_turtle=_dump_subgraph(g, qvs),
            ))
        return shape

    return complex_constraint(path_local, 'other')
