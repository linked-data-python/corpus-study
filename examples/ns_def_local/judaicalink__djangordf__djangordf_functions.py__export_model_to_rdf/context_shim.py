# Context shim (see meta.json): the one name original.py takes from Django,
# `django.conf.settings`, of which the region reads only `BASE_DIR` (the
# default output directory). Django is not in the study venv; BASE_DIR is a
# fixed relative path so that the file the region writes lands in the example
# directory. Identical bindings for both representations.
from types import SimpleNamespace

settings = SimpleNamespace(BASE_DIR=".")
