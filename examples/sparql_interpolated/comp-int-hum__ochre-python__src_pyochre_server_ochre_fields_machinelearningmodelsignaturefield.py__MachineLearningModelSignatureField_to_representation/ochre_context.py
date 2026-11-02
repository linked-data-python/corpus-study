# Context shim (see meta.json), for comp-int-hum/ochre-python@8392c11405
# src/pyochre/server/ochre/fields/machinelearningmodelsignaturefield.py, so the
# region executes outside the Django project.  Identical for both
# representations.  Three names of the module are replaced:
#
#   settings  django.conf.settings, reduced to OCHRE_NAMESPACE, with the default
#             of src/pyochre/env.py (`OCHRE_NAMESPACE = (str, "https://cdh.jhu.edu/")`).
#   reverse   django.urls.reverse: a stand-in for the route of the DRF action
#             `machinelearningmodel-apply` (the project's urlconf is not
#             reproduced; the value only travels into `self.style`).
#   files     importlib.resources.files, with "pyochre" answered by the
#             directory pyochre_pkg/ next to this file (the package is not
#             installed).  Its data/model_visualization_query.sparql is a
#             RECONSTRUCTION: the file is missing from the pinned commit (see its
#             header).  Any other package goes to the real importlib.resources.
from importlib.resources import files as _files
from pathlib import Path


class settings:
    OCHRE_NAMESPACE = "https://cdh.jhu.edu/"


def reverse(viewname, args=None, kwargs=None):
    if viewname == "api:machinelearningmodel-apply":
        return "/api/machinelearningmodel/{}/apply/".format(*args)
    raise LookupError(viewname)


def files(package):
    if package == "pyochre":
        return Path(__file__).resolve().parent / "pyochre_pkg"
    return _files(package)
