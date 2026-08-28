# Context shim (see meta.json): httpx is not installed in the evaluation
# environment.  The region only constructs ``httpx.Client(follow_redirects=
# True)`` and stores it on self; no request is ever issued inside the region.
# Used IDENTICALLY by original.py and translated.ldpy.


class Client:
    def __init__(self, follow_redirects=False, **kwargs):
        self.follow_redirects = follow_redirects
        self.kwargs = kwargs

    def __eq__(self, other):
        return (isinstance(other, Client)
                and self.follow_redirects == other.follow_redirects
                and self.kwargs == other.kwargs)

    def get(self, *args, **kwargs):
        raise NotImplementedError("no network in the evaluation environment")


class HTTPError(Exception):
    pass
