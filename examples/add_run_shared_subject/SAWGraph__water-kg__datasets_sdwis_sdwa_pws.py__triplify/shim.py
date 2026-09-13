# Context shim (see meta.json): subset of datasets/sdwis/sdwa_pws.py from
# SAWGraph/water-kg@032ec413576d55e3220c32aeb3109f55af382837, so the region
# executes outside the package. Identical bindings for both representations.
from datetime import datetime
import pandas as pd
from rdflib import Graph, Namespace

prefixes = {}
prefixes['us_sdwis'] = Namespace('http://sawgraph.spatialai.org/v1/us-sdwis#')
prefixes['us_sdwis_data'] = Namespace('http://sawgraph.spatialai.org/v1/us-sdwis-data#')
prefixes['qudt'] = Namespace('http://qudt.org/schema/qudt/')
prefixes['coso'] = Namespace('http://sawgraph.spatialai.org/v1/contaminoso#')
prefixes['geo'] = Namespace('http://www.opengis.net/ont/geosparql#')
prefixes['sosa'] = Namespace('http://www.w3.org/ns/sosa/')
prefixes['gcx'] = Namespace('http://geoconnex.us/')


def Initial_KG():
    kg = Graph()
    for prefix in prefixes:
        kg.bind(prefix, prefixes[prefix])
    return kg


def get_attributes(row):
    pws = {
        'PWSID': row['PWSID'],
        'ActivityCode': row['PWS_ACTIVITY_CODE'],
        'PopulationServed': row['POPULATION_SERVED_COUNT'],
        'Connections': row['SERVICE_CONNECTIONS_COUNT'],
        'FirstReport': datetime.strptime(row['FIRST_REPORTED_DATE'], '%m/%d/%Y'),
    }

    if pd.notnull(row.PWS_NAME):
        pws['Name'] = row['PWS_NAME']
    if pd.notnull(row.SEASON_BEGIN_DATE):
        pws['SeasonBegin'] = row['SEASON_BEGIN_DATE']
        pws['SeasonEnd'] = row['SEASON_END_DATE']
    if pd.notnull(row.PWS_DEACTIVATION_DATE):
        pws['Deactivation'] = datetime.strptime(row['PWS_DEACTIVATION_DATE'], '%m/%d/%Y')
    if pd.notnull(row.LAST_REPORTED_DATE):
        pws['LastReport'] = datetime.strptime(row['LAST_REPORTED_DATE'], '%m/%d/%Y')

    pwsPrimarySourceLookup = {
        'GW': 'Ground water',
        'GWP': 'Ground water Purchased',
        'SW': 'Surface water',
        'SWP': 'Surface water Purchased',
        'GU': 'Ground water under influence of surface water',
        'GUP': 'Purchased ground water under influence of surface water source',
    }
    if pd.notnull(row.PRIMARY_SOURCE_CODE):
        pws['Source'] = pwsPrimarySourceLookup[row['PRIMARY_SOURCE_CODE']]
        pws['SourceType'] = row.PRIMARY_SOURCE_CODE

    pwsTypeLookup = {
        'CWS': 'Community Water System',
        'TNCWS': 'Transient Community Water System',
        'NTNCWS': 'Nontransient Non-Community Water System',
        'NP': '',
    }
    if row['PWS_TYPE_CODE'] in ['TNCWS', 'NTNCWS']:
        pws['Type'] = 'NCWS'
        pws['Transient'] = row['PWS_TYPE_CODE']
    else:
        pws['Type'] = row['PWS_TYPE_CODE']
    pws['PWSTypeName'] = pwsTypeLookup[row['PWS_TYPE_CODE']]

    if pd.notnull(row.GW_SW_CODE):
        pws['GWSW'] = row['GW_SW_CODE']
    if pd.notnull(row.CDS_ID):
        pws['CDSID'] = str(row['CDS_ID']).replace(' ', '')

    pwsActivityCodeLookup = {
        'A': 'Active',
        'I': 'Inactive',
        'N': 'Non-Public',
        'M': 'Merged',
        'P': 'Potential Future System',
    }
    pws['ActivityCodeLong'] = pwsActivityCodeLookup[pws['ActivityCode']]

    pwsOwnerTypeLookup = {
        'F': 'Federal Government',
        'L': 'Local Government',
        'M': 'Public / Private',
        'N': 'Native American',
        'P': 'Private',
        'S': 'State Government',
    }
    if pd.notnull(row.OWNER_TYPE_CODE):
        pws['Owner'] = pwsOwnerTypeLookup[row['OWNER_TYPE_CODE']]

    return pws


def get_iris(pws):
    iris = {}
    iris['PWS'] = prefixes['gcx']['ref/pws/' + pws['PWSID']]
    if 'CDSID' in pws.keys():
        iris['CDS'] = prefixes['us_sdwis_data']['d.CombinedDistributionSystem.' + pws['CDSID']]
    if 'SourceType' in pws.keys():
        iris['SourceType'] = prefixes['us_sdwis_data']['d.PWS-WaterSourceType.' + pws['SourceType']]
    return iris
