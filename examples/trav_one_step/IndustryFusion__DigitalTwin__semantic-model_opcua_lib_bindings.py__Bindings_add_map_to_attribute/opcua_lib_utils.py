# Context shim (see meta.json): subset of semantic-model/opcua/lib/utils.py
# from IndustryFusion/DigitalTwin@3b40088b88, so the region executes outside
# the package (`import lib.utils as utils`; the package is not installed).
# idtype2String is copied verbatim; nothing else of utils is used by the
# region.  Identical bindings for both representations.


def idtype2String(idtype, basens):
    if idtype == basens['numericID']:
        idt = 'i'
    elif idtype == basens['stringID']:
        idt = 's'
    elif idtype == basens['guidID']:
        idt = 'g'
    elif idtype == basens['opaqueID']:
        idt = 'b'
    else:
        idt = 'x'
        print('Warning no idtype found.')
    return idt
