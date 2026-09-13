"""Validation driver for SAWGraph__water-kg__datasets_sdwis_sdwa_pws.py__triplify.

Establishes semantic equivalence of original.py and translated.ldpy.
"""
import pandas as pd
from rdfeval.harness import run_pair

# Rows chosen to exercise every branch of get_attributes/triplify:
#   row 0: CWS, has name, has deactivation date, has GW_SW_CODE, has CDS_ID,
#          has PRIMARY_SOURCE_CODE, has OWNER_TYPE_CODE, has LAST_REPORTED_DATE.
#   row 1: TNCWS (-> Type NCWS, Transient set), no name, no deactivation date,
#          no GW_SW_CODE, no CDS_ID, no PRIMARY_SOURCE_CODE, no OWNER_TYPE_CODE,
#          no LAST_REPORTED_DATE.
_DF = pd.DataFrame([
    {
        'PWSID': 'ME0000123',
        'PWS_ACTIVITY_CODE': 'A',
        'POPULATION_SERVED_COUNT': 500,
        'SERVICE_CONNECTIONS_COUNT': 200,
        'FIRST_REPORTED_DATE': '01/15/1995',
        'PWS_NAME': 'Springvale Water District',
        'SEASON_BEGIN_DATE': None,
        'SEASON_END_DATE': None,
        'PWS_DEACTIVATION_DATE': '06/30/2010',
        'LAST_REPORTED_DATE': '12/31/2020',
        'PRIMARY_SOURCE_CODE': 'GW',
        'PWS_TYPE_CODE': 'CWS',
        'GW_SW_CODE': 'GW',
        'CDS_ID': '123 456',
        'OWNER_TYPE_CODE': 'L',
    },
    {
        'PWSID': 'ME0000456',
        'PWS_ACTIVITY_CODE': 'I',
        'POPULATION_SERVED_COUNT': 25,
        'SERVICE_CONNECTIONS_COUNT': 10,
        'FIRST_REPORTED_DATE': '03/01/2000',
        'PWS_NAME': None,
        'SEASON_BEGIN_DATE': None,
        'SEASON_END_DATE': None,
        'PWS_DEACTIVATION_DATE': None,
        'LAST_REPORTED_DATE': None,
        'PRIMARY_SOURCE_CODE': None,
        'PWS_TYPE_CODE': 'TNCWS',
        'GW_SW_CODE': None,
        'CDS_ID': None,
        'OWNER_TYPE_CODE': None,
    },
])

VERDICT = run_pair(
    __file__,
    entry='triplify',
    calls=[((_DF,), {})],
)
