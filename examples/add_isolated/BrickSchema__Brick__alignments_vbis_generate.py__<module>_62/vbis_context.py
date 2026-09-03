# Context shim (see meta.json): the three module-level helper functions
# this region calls but that live ABOVE it in the source file
# (BrickSchema/Brick@c12949f236, alignments/vbis/generate.py lines 21-57,
# i.e. before the extracted region which starts at line 62), reproduced
# verbatim so the region executes standalone.
#
# Identical bindings for both representations.
import re


def get_brick_class(d):
    for key in ["1", "2", "3", "4", "5"]:
        key = f"Brick Class {key}"
        if d.get(key) and len(d.get(key)) > 0:
            return d.get(key).replace(" ", "_")


def rewrite_vbis_pattern(pat):
    """
    If '*' is in the pattern or there are fewer than 3 '-' in the pattern, then
    we return a rewritten regex; else we return the pattern (which should be a
    fully-qualified VBIS tag).  The first returned value is True if the value
    is a pattern, and False otherwise.

    Rewrite VBIS patterns to match the format of regular expressions
    required by XML schema
    """
    if "*" in pat:
        newpat = "^" + re.sub(r"-?\*", ".*", pat.strip()) + "$"
        return True, newpat
    elif len(re.findall("-", pat)) < 3:
        # treat this as a prefix
        return True, "^" + pat.strip() + ".*$"
    return False, pat


def get_vbis_tags(d):
    vbis_tags = []
    for key in [
        "VBIS Tag",
        "Other VBIS Asset Types #1",
        "Other VBIS Asset Types #2",
        "Other VBIS Asset Types #3",
    ]:
        if d.get(key) and len(d.get(key)) > 0:
            vbis_tags.append(d.get(key))
    return vbis_tags
