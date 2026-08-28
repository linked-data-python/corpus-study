"""Context shim for the RDFLib/pyLODE ``Query.load_component_model`` region.

The region is a method of ``pylode/profiles/supermodel/query/__init__.py``.
Lifted out of that file it needs (a) the model dataclasses and the
``query.common`` helpers it imports, and (b) four helper functions that were
plain siblings in the same module and therefore have no import line of their
own: ``get_component_model_ignored_classes``, ``get_top_level_component_classes``,
``get_examples`` and ``get_rdf_properties``.

Everything here is the REAL pyLODE code, executed straight from the corpus
checkout (RDFLib/pyLODE@0d0471fb99).  Two mechanical obstacles are worked
around, neither of which touches any code path the region uses:

* ``pylode/__init__.py`` and ``pylode/utils.py`` pull in packages that are
  not installed in the evaluation venv (dominate, jinja2, markdown, httpx,
  tqdm, kurra) — they are registered as inert stub modules;
* ``pylode/version.py`` reads installed distribution metadata — it is
  replaced by a stub exporting ``__version__``.

The parent packages are registered as namespace packages so that
``pylode/__init__.py`` is never executed.

This module is imported IDENTICALLY by original.py and translated.ldpy.
"""

import importlib.util
import sys
import types
from pathlib import Path

_ROOT = Path(
    "/home/lefrancois/Documents/recherche/semantic_web_micropython/github"
    "/corpus/repos/RDFLib__pyLODE"
)


class _InertModule(types.ModuleType):
    """Stand-in for an absent third-party package: every attribute is a class."""

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)
        return type(name, (), {"__init__": lambda self, *a, **k: None,
                               "__call__": lambda self, *a, **k: None})


def _install_stubs() -> None:
    for name in ("httpx", "tqdm", "dominate", "dominate.tags", "dominate.util",
                 "markdown", "jinja2", "kurra", "kurra.labels", "kurra.utils",
                 "kurra.sparql", "kurra.format", "kurra.file", "kurra.db"):
        if name not in sys.modules:
            mod = _InertModule(name)
            mod.__path__ = []
            sys.modules[name] = mod
    sys.modules["tqdm"].tqdm = lambda it=None, *a, **k: it

    for pkg, rel in (("pylode", "pylode"),
                     ("pylode.profiles", "pylode/profiles"),
                     ("pylode.profiles.supermodel", "pylode/profiles/supermodel"),
                     ("pylode.profiles.supermodel.query",
                      "pylode/profiles/supermodel/query")):
        if pkg not in sys.modules:
            mod = types.ModuleType(pkg)
            mod.__path__ = [str(_ROOT / rel)]
            sys.modules[pkg] = mod

    if "pylode.version" not in sys.modules:
        version = types.ModuleType("pylode.version")
        version.__version__ = "0.0.0"
        sys.modules["pylode.version"] = version


def _load_query_module():
    name = "pylode.profiles.supermodel.query"
    path = _ROOT / "pylode/profiles/supermodel/query/__init__.py"
    spec = importlib.util.spec_from_file_location(
        name, path,
        submodule_search_locations=[str(path.parent)])
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_install_stubs()
_query = _load_query_module()
_model = sys.modules["pylode.profiles.supermodel.model"]
_common = sys.modules["pylode.profiles.supermodel.query.common"]
LODE = sys.modules["pylode.profiles.supermodel.namespace"].LODE

# --- names the region imports from pylode.profiles.supermodel.model ---------
Class = _model.Class
CodedProperty = _model.CodedProperty
ComponentModel = _model.ComponentModel
ImageObject = _model.ImageObject
MediaObject = _model.MediaObject
Note = _model.Note
Profile = _model.Profile
ProfileHierarchyItem = _model.ProfileHierarchyItem
ProfileType = _model.ProfileType
Property = _model.Property
RDFProperty = _model.RDFProperty
Resource = _model.Resource
SimpleCodedProperty = _model.SimpleCodedProperty
TextObject = _model.TextObject

# --- names the region imports from ...query.common -------------------------
get_class = _common.get_class
get_descriptions = _common.get_descriptions
get_is_defined_by = _common.get_is_defined_by
get_name = _common.get_name
get_subclasses = _common.get_subclasses
get_values = _common.get_values

# --- siblings of the region in ...query/__init__.py (no import line there) --
get_component_model_ignored_classes = _query.get_component_model_ignored_classes
get_examples = _query.get_examples
get_rdf_properties = _query.get_rdf_properties
get_top_level_component_classes = _query.get_top_level_component_classes
