"""Context shim (see meta.json) for `kgcl_schema.grammar.parser`.

The real `kgcl-schema` package (a lark grammar over the whole KGCL language)
is not installable in the evaluation environment.  This stub recognises the
single KGCL command the demo harness uses --

    rename <IRI> from 'old label' to 'new label'

-- and returns the same shape of value as the real parser: a list of change
objects with `about_node` / `old_value` / `new_value` / `*_language` fields.
It is imported IDENTICALLY by original.py and translated.ldpy.
"""

import re

_RENAME = re.compile(
    r"^\s*rename\s+(?P<about><[^>]*>|\S+:\S+)\s+"
    r"from\s+(?P<old>'[^']*')\s+to\s+(?P<new>'[^']*')\s*$"
)


class NodeRename:
    """Mirrors the fields of kgcl_schema.datamodel.kgcl.NodeRename."""

    def __init__(self, about_node, old_value, new_value,
                 old_language=None, new_language=None):
        self.about_node = about_node
        self.old_value = old_value
        self.new_value = new_value
        self.old_language = old_language
        self.new_language = new_language


def parse(text):
    """Parse KGCL commands (one per line); returns a list of change objects."""
    changes = []
    for line in text.splitlines():
        if not line.strip():
            continue
        m = _RENAME.match(line)
        if m is None:
            raise ValueError("shim parser: unsupported KGCL command %r" % line)
        changes.append(NodeRename(m.group("about"), m.group("old"),
                                  m.group("new")))
    return changes
