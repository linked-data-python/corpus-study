# Context shim (see meta.json): subset of ktbs/ktbs@4f9f50c770, so the region
# executes outside the package (the `..namespace` relative import and the
# class `Method` the region names in `super(Method, self)` are not there).
# Identical bindings for both representations.
#
# KTBS: lib/ktbs/namespace.py's namespace IRI (a ClosedNamespace built from
#   the ontology there; the closure is irrelevant here, hence a plain
#   Namespace).
# Diagnosis: lib/rdfrest/util/__init__.py, class Diagnosis, verbatim minus the
#   `&` operators the region does not use.
# _LocalCore.check_deletable: lib/rdfrest/cores/local.py, LocalCore.check_deletable
#   (the default always accepts).
# Method: only what the region needs of ktbs.engine.method.Method: `uri` and
#   `state` (a read-only graph in the real class) given at construction.
from rdflib import Namespace

KTBS = Namespace("http://liris.cnrs.fr/silex/2009/ktbs#")

# what `from ktbs_context import ktbs:` reads
__namespaces__ = {"ktbs": KTBS}


class Diagnosis(object):
    """I contain a list of problems and eval to True if there is no problem.
    """
    def __init__(self, title="diagnosis", errors=None, traceback=None):
        self.title = title
        if errors is None:
            errors = []
        else:
            errors = list(errors)
        self.errors = errors
        self.traceback = traceback

    def __bool__(self):
        return len(self.errors) == 0

    def __iter__(self):
        return iter(self.errors)

    def __str__(self):
        if self.errors:
            return "%s: ko\n* %s\n" % (self.title, "\n* ".join(self.errors))
        else:
            return "%s: ok" % self.title

    def __repr__(self):
        return "Diagnosis(%r, %r)" % (self.title, self.errors)

    def append(self, error_msg):
        """Append a problem to this diagnosis.
        """
        self.errors.append(error_msg)


class _LocalCore(object):
    def check_deletable(self, parameters):
        """I implement :meth:`.ILocalCore.check_deletable`.

        The default always accepts.
        """
        return Diagnosis("check_deletable")


class Method(_LocalCore):
    def __init__(self, uri, state):
        self.uri = uri
        self.state = state
