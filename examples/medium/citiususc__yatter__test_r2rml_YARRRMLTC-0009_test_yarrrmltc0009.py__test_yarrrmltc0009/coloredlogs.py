# Context shim (see meta.json): `yatter.constants` does
# `import logging, coloredlogs` and then `coloredlogs.install(..., logger=...)`
# purely to colourise its log output.  coloredlogs is not part of the
# evaluation environment, so this no-op stand-in is placed on sys.path ahead of
# it.  It affects log formatting only, never RDF behaviour, and it is imported
# identically by both representations (they run in the same process).


def install(*args, **kwargs):
    return None


def set_level(*args, **kwargs):
    return None
