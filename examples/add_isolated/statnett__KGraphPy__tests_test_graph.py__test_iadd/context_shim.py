# Context shim (see meta.json): makes `kgraphpy` importable outside its
# repository. kgraphpy (statnett/KGraphPy@38859be62f) is not installed in the
# study venv: it is imported from the pinned clone made by `rdfeval acquire`
# (corpus/repos/statnett__KGraphPy), i.e. the REAL CIMGraph / CIMProcessor /
# Provenance code runs, unmodified.
#
# kgraphpy.processor / enriching / cimxml_parser also import SchemaView and
# a few model classes from `linkml_runtime`, which is not installed either.
# This region never touches them (they serve CIMProcessor.set_schema and the
# CIM XML parser only), so when the real package is absent an empty module
# with the imported names is registered in its place. If linkml_runtime is
# installed, the real one is used and nothing is stubbed.
# Identical bindings for both representations.
import importlib
import sys
import types
from pathlib import Path

_CLONE = Path(__file__).resolve().parents[3] / "corpus" / "repos" / "statnett__KGraphPy"
if str(_CLONE) not in sys.path:
    sys.path.insert(0, str(_CLONE))

try:
    importlib.import_module("linkml_runtime.utils.schemaview")
    importlib.import_module("linkml_runtime.linkml_model.meta")
except ImportError:
    def _module(name, **names):
        mod = types.ModuleType(name)
        mod.__dict__.update(names)
        sys.modules[name] = mod
        return mod

    class SchemaView:                       # only named, never called here
        pass

    class SchemaDefinition:
        pass

    class SlotDefinition:
        pass

    class TypeDefinition:
        pass

    for _name in ("linkml_runtime", "linkml_runtime.utils", "linkml_runtime.linkml_model"):
        _module(_name)
    _module("linkml_runtime.utils.schemaview", SchemaView=SchemaView,
            SchemaDefinition=SchemaDefinition, SlotDefinition=SlotDefinition)
    _module("linkml_runtime.linkml_model.meta", TypeDefinition=TypeDefinition)
