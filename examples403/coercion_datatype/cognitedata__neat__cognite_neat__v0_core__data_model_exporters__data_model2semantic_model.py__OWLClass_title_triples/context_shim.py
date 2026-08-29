# Context shim (see meta.json): a minimal reconstruction of OWLClass and
# remove_namespace_from_uri from cognitedata/neat@4042d3e96d :
# cognite/neat/_v0/core/_data_model/exporters/_data_model2semantic_model.py
# and cognite/neat/_v0/core/_utils/rdf_.py, so the region executes outside the
# package (cognite.neat pulls in pydantic and the cognite SDK, neither
# installed in the study venv). Identical bindings for both representations.
#
# OWLClass is reduced to the two fields title_triples reads (id_, label); the
# real class is a pydantic BaseModel with more fields (type_, comment,
# sub_class_of, namespace) not needed to exercise this property.
#
# remove_namespace_from_uri is reduced to the single-URI, default-validation
# ("prefix") branch the region exercises: split on "#_" if present, else "#",
# else "/", keep the last segment. The "full" pydantic-validated branch and
# the sequence-of-URIs overload are not reached by this region.


class OWLClass:
    def __init__(self, id_, label):
        self.id_ = id_
        self.label = label


def remove_namespace_from_uri(uri, *, special_separator="#_"):
    u = str(uri)
    if u.lower().startswith("http"):
        sep = special_separator if special_separator in u else ("#" if "#" in u else "/")
        return u.split(sep)[-1]
    return u
