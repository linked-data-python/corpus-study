# Extracted from ktbs/ktbs@4f9f50c770 : lib/ktbs/plugins/meth_external.py
# region: _ExternalMethod.compute_trace_description (lines 46-80, stratum ns_import_project)
# licence of the source repository: see meta.json
from rdflib import Literal, Graph, URIRef
from rdfrest.util import Diagnosis
from ktbs.namespace import KTBS

def compute_trace_description(self, computed_trace):
    """I implement :meth:`.interface.IMethod.compute_trace_description`.
    """
    diag = Diagnosis("external.compute_trace_description")

    srcs, params =  self._prepare_sources_and_params(computed_trace, diag)
    if srcs is not None:

        assert params is not None
        model = params.get("model")
        if model is not None:
            model = URIRef(model)
        else:
            models = set( src.model_uri for src in srcs )
            if len(models) != 1:
                diag.append("Can not infer model from sources and no "
                            "target model is explicitly specified")
            else:
                model = models.pop()

        origin = params.get("origin")
        if origin is None:
            origins = set( src.origin for src in srcs )
            if len(origins) != 1:
                diag.append("Can not infer origin from sources and no "
                            "target origin is explicitly specified")
            else:
                origin = origins.pop()
        origin = Literal(origin)

        with computed_trace.edit(_trust=True) as editable:
            editable.add((computed_trace.uri, KTBS.hasModel, model))
            editable.add((computed_trace.uri, KTBS.hasOrigin, origin))

    return diag
