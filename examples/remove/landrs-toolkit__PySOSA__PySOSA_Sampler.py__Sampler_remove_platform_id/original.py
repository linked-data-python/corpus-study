# Extracted from landrs-toolkit/PySOSA@1993668bd7 : PySOSA/Sampler.py
# region: Sampler.remove_platform_id (lines 48-54, stratum remove)
# licence of the source repository: see meta.json
from PySOSA import config as cfg
obsgraph = Graph()

def remove_platform_id(self, Sampler):
    """
    remove platform id
    """
    sampler_uri = Sampler.get_uri()
    self.samplings.remove(Sampler.platform_id)
    obsgraph.remove((self.platform_id, cfg.sosa.hosts, sampler_uri))
