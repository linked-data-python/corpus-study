# Context shim (see meta.json): subset of app/models/aas_namespace.py,
# app/models/has_extensions.py, app/models/lang_string_name_type.py and
# app/models/lang_string_text_type.py from
# mhrimaz/aasbrain-concept-description-repo@46ae59a87e, so the region
# executes outside the package. Identical bindings for both representations.
from typing import List, Optional

import rdflib
from pydantic import BaseModel, Field
from rdflib import RDF
from rdflib.namespace import Namespace


class AASNameSpace:
    AAS = Namespace("https://admin-shell.io/aas/3/0/")


class LangStringNameType(BaseModel):
    language: Optional[str] = None
    text: Optional[str] = None


class LangStringTextType(BaseModel):
    language: Optional[str] = None
    text: Optional[str] = None


class HasExtensions(BaseModel):
    extensions: Optional[List[object]] = Field(None)

    @staticmethod
    def from_rdf(graph: rdflib.Graph, subject: rdflib.IdentifiedNode):
        # The region under study is Referable.from_rdf; HasExtensions.from_rdf
        # is context, kept to its own single one-step read since a fixture
        # with no extensions exercises the zero-solution branch faithfully.
        extensions = []
        for extension_ref in graph.objects(
            subject=subject, predicate=AASNameSpace.AAS["HasExtensions/extensions"]
        ):
            extensions.append(str(extension_ref))
        if len(extensions) == 0:
            extensions = None
        return HasExtensions(extensions=extensions)


class Referable(HasExtensions):
    category: Optional[str] = None
    idShort: Optional[str] = None
    displayName: Optional[List[LangStringNameType]] = Field(None)
    description: Optional[List[LangStringTextType]] = Field(None)
