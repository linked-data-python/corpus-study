# Context shim (see meta.json): the region reads exactly one setting from
# mariocosenza/kgsum@320b14fc57 config.py -- Config.QUERY_LOV -- kept at its
# upstream default (True).  The rest of the class (secrets, classifier
# selection, phase machinery, config.json loading) is irrelevant here.
# Identical for both representations.


class Config:
    QUERY_LOV: bool = True
