# Extracted from usc-gria/sw-kg@08db325932 : teams/pela/TAREA_6/src/preprocess.py
# region: preprocess (lines 58-108, stratum sparql_literal)
# licence of the source repository: see meta.json
import os
import pandas as pd
from rdflib import Graph
from preprocess_shim import DATA_DIR, KG_PATH, get_wikidata_info

def preprocess():
    g = Graph()
    print(f"Cargando {KG_PATH}...")
    g.parse(KG_PATH, format='nt')
    print("Extrayendo datos locales...")

    # Query 1: Campos
    df_fields = pd.DataFrame([{ 'id': str(r.id), 'nombre': str(r.nombre), 'x': float(r.x), 'y': float(r.y), 'distrito': str(r.distrito), 'wdDistrito': str(r.wdDistrito) if r.wdDistrito else None } for r in g.query(
        "PREFIX ns: <https://example.org/partidos/> SELECT ?id ?nombre ?x ?y ?distrito ?wdDistrito WHERE { ?id a ns:Campo ; ns:nombreCampo ?nombre ; ns:coorX ?x ; ns:coorY ?y ; ns:localizadoEn ?d . ?d ns:nombreDistrito ?distrito . OPTIONAL { ?d ns:sameAsDistrito ?wdDistrito } }")])

    # Query 2: Partidos
    print("Extrayendo partidos...")
    df_matches = pd.DataFrame([{ 'partido': str(r.partido), 'campoId': str(r.campoId), 'local': str(r.local), 'visitante': str(r.visitante), 'resultado': f"{r.res1}-{r.res2}", 'fecha': str(r.fecha)[:10] } for r in g.query(
        "PREFIX ns: <https://example.org/partidos/> SELECT ?partido ?campoId ?local ?visitante ?res1 ?res2 ?fecha WHERE { ?partido ns:ocurreEn ?campoId ; ns:tieneEquipoLocal ?el . ?el ns:nombreEquipo ?local . ?partido ns:tieneEquipoVisitante ?ev . ?ev ns:nombreEquipo ?visitante . ?partido ns:resultado1 ?res1 ; ns:resultado2 ?res2 ; ns:hora ?fecha }")])

    # Query 3: Partidos con deporte
    print("Vinculando partidos con deportes...")
    df_ms = pd.DataFrame([{ 'partido': str(r.partido), 'deporte': str(r.nombreDeporte), 'wdDeporte': str(r.wdDeporte) if r.wdDeporte else None } for r in g.query(
        "PREFIX ns: <https://example.org/partidos/> SELECT ?partido ?nombreDeporte ?wdDeporte WHERE { ?jornada ns:tienePartido ?partido . ?grupo ns:tieneJornada ?jornada . ?competicion ns:tieneGrupo ?grupo ; ns:tipoDe ?deporte . ?deporte ns:nombreDeporte ?nombreDeporte . OPTIONAL { ?deporte ns:sameAsDeporte ?wdDeporte } }")])
    df_matches = df_matches.merge(df_ms, on='partido', how='left')

    def wikidata_column(uris, info, key):
        return uris.map(lambda x: info.get(x, {}).get(key) if pd.notna(x) else None)

    print("Buscando información en Wikidata para distritos...")
    wd_dist_info = get_wikidata_info(df_fields['wdDistrito'].unique(),
        "SELECT ?item ?poblacion ?imagen WHERE { VALUES ?item { {{VALUES}} } OPTIONAL { ?item wdt:P1082 ?poblacion . } OPTIONAL { ?item wdt:P18 ?imagen . } }")

    # Mapeo vectorizado de datos de Wikidata a los distritos
    df_fields['poblacion'] = wikidata_column(df_fields['wdDistrito'], wd_dist_info, 'poblacion')
    df_fields['distrito_imagen'] = wikidata_column(df_fields['wdDistrito'], wd_dist_info, 'imagen')

    print("Buscando información en Wikidata para deportes...")
    # Usamos schema:description para una descripción real, no solo el label
    wd_sport_info = get_wikidata_info(df_matches['wdDeporte'].unique(), """
    SELECT ?item ?descripcion ?imagen WHERE { 
      VALUES ?item { {{VALUES}} } 
      OPTIONAL { 
        ?item schema:description ?descripcion . 
        FILTER(LANG(?descripcion) = 'es') 
      } 
      OPTIONAL { ?item wdt:P18 ?imagen . } 
    }
    """)

    # Mapeo vectorizado de descripciones e imágenes de deportes
    df_matches['deporte_descripcion'] = wikidata_column(df_matches['wdDeporte'], wd_sport_info, 'descripcion')
    df_matches['deporte_imagen'] = wikidata_column(df_matches['wdDeporte'], wd_sport_info, 'imagen')

    os.makedirs(DATA_DIR, exist_ok=True)
    df_fields.to_csv(os.path.join(DATA_DIR, 'fields.csv'), index=False)
    df_matches.to_csv(os.path.join(DATA_DIR, 'matches.csv'), index=False)
    print("¡Listo!")
