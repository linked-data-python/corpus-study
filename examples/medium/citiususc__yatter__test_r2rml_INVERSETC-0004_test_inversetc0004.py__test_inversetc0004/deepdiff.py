# Context shim (see meta.json): the region imports DeepDiff from the deepdiff
# package, which is not part of the evaluation environment.  The region uses it
# in exactly one way -- DeepDiff(a, b, ignore_order=True) evaluated for truth --
# so this stand-in provides an order-insensitive deep comparison of the plain
# dict/list/scalar structures that ruamel.yaml produces, returning an empty
# (falsy) result when the two structures match and a non-empty (truthy) one
# otherwise.  It is a behavioural stand-in, not a copy of deepdiff.  Both
# representations import it identically (they run in the same process), so the
# equivalence verdict does not depend on it.
import json


def _canonical(value):
    """Order-insensitive canonical form of a JSON-like structure."""
    if isinstance(value, dict):
        return {k: _canonical(v) for k, v in sorted(value.items(), key=repr)}
    if isinstance(value, (list, tuple, set)):
        items = [_canonical(v) for v in value]
        return sorted(items, key=lambda v: json.dumps(v, sort_keys=True, default=str))
    return value


class DeepDiff(dict):
    """Minimal DeepDiff(..., ignore_order=True) stand-in (see module comment)."""

    def __init__(self, t1, t2, ignore_order=False, **kwargs):
        super().__init__()
        if not ignore_order:
            raise NotImplementedError(
                "this stand-in only implements DeepDiff(..., ignore_order=True)")
        c1, c2 = _canonical(t1), _canonical(t2)
        if c1 != c2:
            self["values_changed"] = {"root": {"old_value": c1, "new_value": c2}}
