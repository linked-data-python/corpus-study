# Context shim (see meta.json): kif_lib/namespace/wikibase.py from
# IBM/kif@4ce99d0d9b (Apache-2.0), reduced to the three terms the region uses
# and with its relative import redirected to kif_shim.  Used by original.py;
# translated.ldpy replaces these accesses by prefixed-name islands and no
# longer needs the module.
# Copyright (C) 2023-2025 IBM Corp.
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from kif_shim import DefinedNamespace, Namespace, URIRef


class WIKIBASE(DefinedNamespace):
    """The Wikibase namespace."""

    _NS = Namespace('http://wikiba.se/ontology#')
    DeprecatedRank: URIRef
    NormalRank: URIRef
    PreferredRank: URIRef
