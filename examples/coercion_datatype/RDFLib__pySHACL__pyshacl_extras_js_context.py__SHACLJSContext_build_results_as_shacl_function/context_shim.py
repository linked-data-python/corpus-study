# Context shim (see meta.json): stand-in for `pyduktape2.JSProxy`, the
# proxy pySHACL's pyshacl/extras/js/context.py (RDFLib/pySHACL@469cca7a22)
# imports from the Duktape binding, which is not installed in the study venv.
# The region only does `isinstance(res, JSProxy)` and `res.toPython()`: on a
# real proxy, an attribute the JS object does not define raises AttributeError,
# which the region catches. Same bindings for both representations.
class JSProxy:
    def __init__(self, *value):
        self._value = value

    def toPython(self):
        if not self._value:
            raise AttributeError("toPython")
        return self._value[0]
