# Context shim (see meta.json): AliasingDefinedNamespace, verbatim from
# Display-Lab/scaffold@d368cfe17c : src/utils/namespace/__init__.py, so the
# region executes outside the package (`src.utils.namespace` is not an
# installable/importable package here).  Identical binding for both
# representations -- see meta.json for why this region, unlike its two
# siblings in this stratum, is NOT translated with `from module import p:`.
from rdflib.namespace import (
    _DFNS_RESERVED_ATTRS,
    DefinedNamespace,
    DefinedNamespaceMeta,
)
from rdflib.term import URIRef


class AliasingDefinedNamespaceMeta(DefinedNamespaceMeta):
    _fail = True
    _alias: dict = {}

    _DFNS_RESERVED_ATTRS.add("_alias")

    def __getitem__(cls, name: str, default=None) -> URIRef:
        name_or_alias = cls._alias.get(name, name)
        return super().__getitem__(name_or_alias)


class AliasingDefinedNamespace(
    DefinedNamespace, metaclass=AliasingDefinedNamespaceMeta
):
    """Shorthand for defined namespace classes that use aliases."""

    pass
