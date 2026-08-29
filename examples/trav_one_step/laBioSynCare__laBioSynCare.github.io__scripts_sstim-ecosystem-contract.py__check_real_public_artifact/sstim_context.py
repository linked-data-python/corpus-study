# Context shim (see meta.json): subset of scripts/sstim-ecosystem-contract.py
# from laBioSynCare/laBioSynCare.github.io@6dd8224b034b721c5faf5e515a02658f18aafb24
# (line 416, verified against the file at that commit), so the region
# executes without the rest of that 1700-line script. Identical bindings for
# both representations.
def require(condition: bool, message: str, errors: list) -> None:
    if not condition:
        errors.append(message)
