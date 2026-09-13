# Context shim (see meta.json): no-op stand-in for python-dotenv, which is
# not installed in this sandbox. load_dotenv() does nothing here since no
# .env file is provided or needed for the region's behaviour.
# Identical bindings for both representations.
def load_dotenv(*args, **kwargs):
    return False
