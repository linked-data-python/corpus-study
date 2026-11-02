# Context shim (see meta.json): subset of pyscal/atomRDF@c9b070e15f, so the
# region executes outside the package (atomrdf is not installed here).
# Identical bindings/behaviour for both representations.
#
# atomrdf/namespace.py: plain Namespace(...) bindings, real IRIs, verified
# against the pinned commit.
#
# atomrdf/utils.py: get_material(kg, sample_id) verbatim
# (`return kg.value(sample_id, CMSO.hasMaterial)`; the `str -> URIRef`
# coercion branch is not reachable from this region's own calls, which
# always pass a URIRef sample, but is kept for fidelity).
#
# atomrdf/datamodels/basemodels.py: BaseModel/TemplateMixin subset needed to
# instantiate GrainBoundary (the `_safe_add_triple`/`_has_data`/`template`
# helpers are not reached by from_graph or its demo and are left out, not
# simplified).
#
# atomrdf/datamodels/defects/grainboundary.py: GrainBoundary's own fields and
# its `_read_gb` classmethod, copied verbatim -- `from_graph` (this region)
# calls `cls._read_gb(...)`, so it must exist for the region to run at all.
from typing import Any, List, Optional
from rdflib import Namespace, XSD

CMSO = Namespace("http://purls.helmholtz-metadaten.de/cmso/")
PLDO = Namespace("http://purls.helmholtz-metadaten.de/cdos/pldo/")
CDCO = Namespace("http://purls.helmholtz-metadaten.de/cdos/cdco/")


def get_material(kg, sample_id):
    from rdflib import URIRef
    if isinstance(sample_id, str):
        sample_id = URIRef(sample_id)
    return kg.value(sample_id, CMSO.hasMaterial)


from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, field_validator


def remove_empty_dicts(data):
    if isinstance(data, dict):
        cleaned = {}
        for k, v in data.items():
            cleaned_v = remove_empty_dicts(v)
            if isinstance(cleaned_v, dict) and cleaned_v == {}:
                continue
            if cleaned_v is None:
                continue
            if isinstance(cleaned_v, list) and cleaned_v == []:
                continue
            cleaned[k] = cleaned_v
        return cleaned
    elif isinstance(data, list):
        return [remove_empty_dicts(v) for v in data]
    else:
        return data


class BaseModel(PydanticBaseModel):
    def __init__(__pydantic_self__, **data: Any):
        cleaned = remove_empty_dicts(data)
        super().__init__(**cleaned)


class TemplateMixin:
    id: Optional[str] = Field(default=None, description="ID in the graph")
    label: Optional[str] = Field(default=None, description="Label in the graph")

    @field_validator("label", mode="before")
    @classmethod
    def _convert_label_list_to_string(cls, v):
        if isinstance(v, list):
            return ". ".join(str(item) for item in v)
        return v


class GrainBoundary(TemplateMixin, BaseModel):
    sigma: Optional[int] = None
    plane: Optional[List[float]] = None
    misorientation_angle: Optional[float] = None
    rotation_axis: Optional[List[float]] = None

    @classmethod
    def _read_gb(cls, graph, sample, plane_defect):
        sigma = graph.value(plane_defect, PLDO.hasSigmaValue)
        plane = graph.value(plane_defect, PLDO.hasGBplane)
        rotation_axis = graph.value(plane_defect, PLDO.hasRotationAxis)
        misorientation_angle = graph.value(plane_defect, PLDO.hasMisorientationAngle)

        return cls(
            sigma=int(sigma) if sigma is not None else None,
            plane=[float(x) for x in plane.split()] if plane is not None else None,
            rotation_axis=(
                [float(x) for x in rotation_axis.split()]
                if rotation_axis is not None
                else None
            ),
            misorientation_angle=(
                float(misorientation_angle)
                if misorientation_angle is not None
                else None
            ),
        )
