"""Validation driver for RDFLib__pySHACL__pyshacl_extras_js_context.py__SHACLJSContext_build_results_as_shacl_function.

`build` is the restored callable (original.py / translated.ldpy end with the
same alias of the classmethod). The region takes a Python value coming out of
a JavaScript function and returns an RDF term; every call below reaches one
branch, and the typed-literal ones are where the coercion lives:

  * a proxy (JSProxy with a value, JSProxy without `toPython`) and the
    pass-through of an existing term: nothing built;
  * float / Decimal with no return type -> `Literal(str(res), XSD.decimal)`,
    including the values whose lexical form rdflib normalises
    (`1e-05` -> `0.00001`, `inf` -> `Infinity`), which a hand-written lexical
    form would not;
  * bool with no return type -> `Literal(res, XSD.boolean)` ("true", never
    "True"), against a bool WITH a return type (first typed branch, where the
    lexical form is `str(True)` and normalisation is off);
  * int / float with a return type -> lexical form kept as written
    (`5` double stays `5`, not `5.0`);
  * str / bytes / int with or without a return type -> `normalize=False`
    (`05` integer stays `05`);
  * a value no branch knows (None, a list) is returned as is.
"""
from decimal import Decimal

from rdflib import BNode, Literal, URIRef
from rdflib.namespace import XSD

from context_shim import JSProxy
from rdfeval.harness import run_pair

B = BNode("keep")

VERDICT = run_pair(
    __file__,
    entry="build",
    calls=[
        # proxies and terms
        ((JSProxy(42),), {}),
        ((JSProxy("a string"), XSD.integer), {}),
        ((JSProxy(),), {}),
        ((Literal("x", lang="en"),), {}),
        ((URIRef("http://example.org/a"), XSD.double), {}),
        ((B,), {}),
        # float / Decimal, no return type -> xsd:decimal
        ((1.5,), {}),
        ((1e-05,), {}),
        ((float("inf"),), {}),
        ((Decimal("1.50"),), {}),
        ((Decimal("1E+3"),), {}),
        # Decimal reaches the decimal branch even with a return type
        ((Decimal("2.5"), XSD.double), {}),
        # bool, no return type -> xsd:boolean ; with one -> first branch
        ((True,), {}),
        ((False,), {}),
        ((True, XSD.integer), {}),
        # int / float with a return type: lexical form as written
        ((5, XSD.double), {}),
        ((2.5, XSD.float), {}),
        ((1e-05, XSD.decimal), {}),
        # int, str, bytes without / with a return type: normalize=False
        ((7,), {}),
        (("hello",), {}),
        ((b"bytes",), {}),
        (("05", XSD.integer), {}),
        (("5", XSD.double), {}),
        (("true", XSD.boolean), {}),
        (("True", XSD.boolean), {}),
        ((b"12", XSD.integer), {}),
        # no branch: returned unchanged
        ((None,), {}),
        (([1, 2], XSD.integer), {}),
    ],
)
