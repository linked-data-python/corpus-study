#!/usr/bin/env python3
# Stand-in for landscape/07-tooling/enrichment_c_v2_0_0.py of
# altunelyusuf/SemanticTechnologies@bad0fa7c46: only REL_PROPS (the relation
# properties minted in the v2 TBox), copied verbatim; the region reads its keys.
REL_PROPS = {
 "buildsOn": ("builds on", "This property links a subject area to a foundational subject area whose concepts it presupposes.", True),
 "standardizedBy": ("standardized by", "This property links a subject area to the standards chapter area where its normative specifications live.", False),
 "implementedBy": ("implemented by", "This property links a subject area to the ecosystem area whose products or libraries implement it.", False),
 "governedBy": ("governed by", "This property links a subject area to the regulatory area whose obligations constrain it.", False),
 "informs": ("informs", "This property links a subject area to another area whose design or operation its findings shape.", False),
 "stewardedBy": ("stewarded by", "This property links a subject area to the bodies chapter area that stewards its artifacts.", False),
}
EXT2 = {}
MARKER_EXT = {}
