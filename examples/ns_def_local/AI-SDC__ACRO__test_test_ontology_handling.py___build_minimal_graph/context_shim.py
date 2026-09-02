# Context shim (see meta.json): the two names original.py imports from
# acro.ontology_handler that _build_minimal_graph actually needs (PREFIX,
# the base namespace string) plus stand-ins for the rest of the import list
# so the statement itself still executes -- the region never calls them.
# From AI-SDC/ACRO@eb1d6e370a : acro/ontology_handler.py. Identical bindings
# for both representations.
PREFIX = "https://example.org/acro-ontology#"


def is_uri(*args, **kwargs):
    raise NotImplementedError("not used by this region")


def make_ischeckedby(*args, **kwargs):
    raise NotImplementedError("not used by this region")


def make_ismitigatedby(*args, **kwargs):
    raise NotImplementedError("not used by this region")


def make_save_analyses(*args, **kwargs):
    raise NotImplementedError("not used by this region")


def make_save_risks(*args, **kwargs):
    raise NotImplementedError("not used by this region")


def make_save_statbarns(*args, **kwargs):
    raise NotImplementedError("not used by this region")


def populate_useful_dicts(*args, **kwargs):
    raise NotImplementedError("not used by this region")


def print_nested_dict(*args, **kwargs):
    raise NotImplementedError("not used by this region")
