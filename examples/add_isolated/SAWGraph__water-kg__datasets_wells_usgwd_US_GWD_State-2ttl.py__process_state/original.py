# Extracted from SAWGraph/water-kg@032ec41357 : datasets/wells/usgwd/US_GWD_State-2ttl.py
# region: process_state (lines 169-230, stratum add_isolated)
# licence of the source repository: see meta.json
import pandas as pd
from rdflib import Graph, Literal
from rdflib.namespace import GEO, RDF, SDO, XSD
logger = logging.getLogger(__name__)

def process_state(state, state_name, shp_file, graph, _PREFIX):
    logger.info(f'Load {state_name} well data from {shp_file}.')
    gdf = load_shapefile(shp_file)
    # print(gdf.columns)
    logger.info(f'Triplify {state_name} well data.')
    for row in gdf.itertuples():
        welliri_base = f'd.USGWD_Well.{str(row.WellID)}'
        welliri, geomiri = build_iris(welliri_base, _PREFIX)
        graph.add((welliri, RDF.type, _PREFIX['hyfo']['WaterWell']))
        graph.add((welliri, _PREFIX['hyfo']['hasPrimaryWellId'], Literal(str(row.WellID), datatype=XSD.string)))
        graph.add((welliri, _PREFIX['hyfo']['hasSecondaryWellId'], Literal(str(row.IDState), datatype=XSD.string)))
        graph.add((welliri, GEO.hasGeometry, geomiri))
        graph.add((welliri, GEO.defaultGeometry, geomiri))
        graph.add((geomiri, RDF.type, GEO.Geometry))
        graph.add((geomiri, GEO.asWKT, Literal(row.geometry, datatype=GEO.wktLiteral)))
        if 'unk' not in row.AquiferSp.lower():
            graph.add((welliri, _PREFIX['hyfo']['tapsAquifer'], Literal(row.AquiferSp, datatype=XSD.string)))
        graph.add((welliri, _PREFIX['kwg-ont']['sfWithin'], _PREFIX['wbd'][f'd.HUC12.{row.HUC12}']))
        if 'unk' not in row.xyVerified.lower():
            graph.add((welliri, _PREFIX['usgwd']['locationVerified'], Literal(row.xyVerified, datatype=XSD.string)))
        graph = add_county_flag(graph, row.F_County, welliri, _PREFIX)
        graph = add_state_flag(graph, row.F_State, welliri, _PREFIX)
        graph = add_us_flag(graph, row.F_US, welliri, _PREFIX)
        if row.WellDepth is not None and not pd.isna(row.WellDepth):
            lengthiri = f'{welliri_base}.totalLength'
            qviri = f'{lengthiri}.QV'
            graph.add((welliri, _PREFIX['hyfo']['hasTotalDepth'], _PREFIX['usgwd'][lengthiri]))
            graph.add((_PREFIX['usgwd'][lengthiri], RDF.type, _PREFIX['hyfo']['TotalDepth']))
            graph.add((_PREFIX['usgwd'][lengthiri], _PREFIX['qudt']['quantityValue'], _PREFIX['usgwd'][qviri]))
            graph.add((_PREFIX['usgwd'][qviri], RDF.type, _PREFIX['qudt']['QuantityValue']))
            graph.add((_PREFIX['usgwd'][qviri], _PREFIX['qudt']['hasUnit'], _PREFIX['unit']['FT']))
            graph.add((_PREFIX['usgwd'][qviri], _PREFIX['qudt']['numericValue'], Literal(row.WellDepth, datatype=XSD.decimal)))
        if row.ScrDepth is not None and not pd.isna(row.ScrDepth):
            depthiri = f'{welliri_base}.constructedDepth'
            qviri = f'{depthiri}.QV'
            graph.add((welliri, _PREFIX['hyfo']['hasCasingDepth'], _PREFIX['usgwd'][depthiri]))
            graph.add((_PREFIX['usgwd'][depthiri], RDF.type, _PREFIX['hyfo']['CasingDepth']))
            graph.add((_PREFIX['usgwd'][depthiri], _PREFIX['qudt']['quantityValue'], _PREFIX['usgwd'][qviri]))
            graph.add((_PREFIX['usgwd'][qviri], RDF.type, _PREFIX['qudt']['qudt:QuantityValue']))
            graph.add((_PREFIX['usgwd'][qviri], _PREFIX['qudt']['hasUnit'], _PREFIX['unit']['FT']))
            graph.add((_PREFIX['usgwd'][qviri], _PREFIX['qudt']['numericValue'], Literal(row.ScrDepth, datatype=XSD.decimal)))
        if row.Capacity is not None and not pd.isna(row.Capacity):
            capiri = f'{welliri_base}.wellYield'
            qviri = f'{capiri}.QV'
            graph.add((welliri, _PREFIX['hyfo']['hasWellYield'], _PREFIX['usgwd'][capiri]))
            graph.add((_PREFIX['usgwd'][capiri], RDF.type, _PREFIX['hyfo']['WellYield']))
            graph.add((_PREFIX['usgwd'][capiri], _PREFIX['qudt']['quantityValue'], _PREFIX['usgwd'][qviri]))
            graph.add((_PREFIX['usgwd'][qviri], RDF.type, _PREFIX['qudt']['qudt:QuantityValue']))
            graph.add((_PREFIX['usgwd'][qviri], _PREFIX['qudt']['hasUnit'], _PREFIX['unit']['GAL_US-PER-MIN']))
            graph.add((_PREFIX['usgwd'][qviri], _PREFIX['qudt']['numericValue'], Literal(row.Capacity, datatype=XSD.decimal)))
        graph.add((welliri, _PREFIX['hyfo']['hasWellStatus'], Literal(row.Status, datatype=XSD.string)))
        if 'unk' not in row.YrConstr.lower():
            graph.add((welliri, _PREFIX['usgwd']['constructedDuring'], Literal(row.YrConstr, datatype=XSD.string)))
        if 'unk' not in row.YrReport.lower():
            graph.add((welliri, _PREFIX['usgwd']['reportedDuring'], Literal(row.YrReport, datatype=XSD.string)))
        graph.add((welliri, _PREFIX['usgwd']['hasUSGSWaterUse'], Literal(f'{row.USGSCateg}', datatype=XSD.string)))
        if 'irr' in row.USGSCateg.lower():
            graph.add((welliri, _PREFIX['usgwd']['hasStateIrrigSubCat'], Literal(f'{row.IrrState}', datatype=XSD.string)))
            graph.add((welliri, _PREFIX['usgwd']['hasUSGWDIrrigSubCat'], Literal(row.IrrUSGWD, datatype=XSD.string)))
        graph.add((welliri, _PREFIX['usgwd']['potable'], Literal(row.Quality.lower(), datatype=XSD.string)))
        graph = add_dup_flag(graph, row.F_Dup, welliri, _PREFIX)
    return graph
