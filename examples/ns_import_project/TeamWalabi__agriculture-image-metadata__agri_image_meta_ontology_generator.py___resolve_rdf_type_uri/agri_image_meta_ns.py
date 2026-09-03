# Context shim (see meta.json): the six Namespace objects the region
# imports from agri_image_meta.utils.namespaces
# (TeamWalabi/agriculture-image-metadata@d34fe77241), re-declared here so
# original.py can import them without the real (non-PyPI) `agri_image_meta`
# package installed. `agri_image_meta.utils.namespaces` fetched verbatim
# from the pinned commit
# (https://raw.githubusercontent.com/TeamWalabi/agriculture-image-metadata/d34fe77241ecc08266756203d0bb5e82ad05066c/agri_image_meta/utils/namespaces.py)
# -- these six IRIs, plus DCAT (not imported by this region, kept out).
# Identical bindings for both representations.
from rdflib import Namespace

AGIMAGE = Namespace("https://w3id.org/agri-image/")
DCT = Namespace("http://purl.org/dc/terms/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
SOSA = Namespace("http://www.w3.org/ns/sosa/")
EXIF = Namespace("https://exiftool.org/TagNames/EXIF.html#")
SH = Namespace("http://www.w3.org/ns/shacl#")
