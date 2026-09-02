# Context shim (see meta.json): two names `Namespace.__getattr__` needs
# that live OUTSIDE the extracted region, restored here verbatim from
# SwissDataScienceCenter/calamus@c59d6fe968:
#
#  - `IRIReference` is a SIBLING top-level class in the SAME file
#    (calamus/fields.py, lines 38-70), defined just above `Namespace` --
#    dropped by the extraction because only the `Namespace.__getattr__`
#    qualname was selected. Transcribed verbatim (rdflib/stdlib-only).
#  - `ONTOLOGY_QUERY` is `calamus/utils.py`'s module-level constant, a
#    `prepareQuery(...)` call. Reproduced directly rather than through its
#    real `LazyProxy` wrapper (calamus/utils.py's `_get_ontology_query` /
#    `LazyProxy(_get_ontology_query)`, from the `lazy_object_proxy` package):
#    the proxy only *defers* the identical `prepareQuery(...)` call to first
#    use for performance ("prepareQuery is rather slow"), which is not part
#    of this region's RDF behaviour -- calling it eagerly here produces the
#    same Query object `Namespace.__getattr__` receives either way.
#
# `Proxy`, `normalize_type`, `normalize_value` are also named in the
# region's own `from calamus.utils import ONTOLOGY_QUERY, Proxy,
# normalize_type, normalize_value` context line (copied verbatim from the
# real file) but are DEAD in `__getattr__`'s body -- it never calls them.
# Stand-ins only, so the import statement resolves; installing the real
# `calamus` package (and its `marshmallow` / `lazy_object_proxy`
# dependencies) for three names this region never touches would be
# scaffolding, not context. calamus IS on PyPI (checked: `pip index
# versions calamus` -> 0.4.3) but is not needed here.
Proxy = None
normalize_type = None
normalize_value = None


from functools import total_ordering

from rdflib.plugins.sparql import prepareQuery


@total_ordering
class IRIReference(object):
    """Represent an IRI in a namespace.

    Args:
        namespace (Namespace): The ``Namespace`` this IRI is part of.
        name (str): the property name of this IRI."""

    def __init__(self, namespace, name):
        self.namespace = namespace
        self.name = name

    def __str__(self):
        """Return expanded string for IRI."""
        return "{namespace}{name}".format(namespace=self.namespace, name=self.name)

    def __repr__(self):
        """Representation of IRI."""
        return 'IRIReference(namespace="{namespace}", name="{name}")'.format(namespace=self.namespace, name=self.name)

    def __eq__(self, other):
        """Check equality between this and an other IRIReference."""
        expanded = str(self)

        if isinstance(other, IRIReference):
            other = str(other)

        return expanded == other

    def __lt__(self, other):
        """Compare this with another IRI."""
        return str(self) < str(other)

    def __hash__(self):
        return str(self).__hash__()


ONTOLOGY_QUERY = prepareQuery(
    "ask { { ?property rdf:type <http://www.w3.org/2002/07/owl#DatatypeProperty> .} UNION { ?property rdf:type "
    "<http://www.w3.org/2002/07/owl#ObjectProperty> .} }"
)
