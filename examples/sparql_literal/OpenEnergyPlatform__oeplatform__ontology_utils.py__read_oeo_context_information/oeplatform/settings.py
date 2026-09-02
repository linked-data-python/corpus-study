# Context shim (see meta.json): the three constants ontology/utils.py imports
# from oeplatform/settings.py in OpenEnergyPlatform/oeplatform@ff28ef6390,
# transcribed verbatim (the real module also pulls in Django app config and
# oeplatform/securitysettings.py, not available in the study venv).
# Identical bindings for both representations.
ONTOLOGY_ROOT = "ontologies"
OPEN_ENERGY_ONTOLOGY_NAME = "oeo"
OEO_EXT_NAME = "oeox"
