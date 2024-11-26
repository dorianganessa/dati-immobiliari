#!/usr/bin/env python3

import os

def create_tables(conn):
    dirname = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(dirname, 'data', 'QI_1106117_1_20241_VALORI.csv')
    filename_luoghi = os.path.join(dirname, 'data', 'QI_1106117_1_20241_ZONE.csv')
    create_prezzi_statement = f"CREATE OR REPLACE TABLE prezzi AS select * from '{filename}'"
    create_luoghi_statement = f"CREATE OR REPLACE TABLE luoghi AS select * from '{filename_luoghi}'"
    create_joined_data_statement = """
    CREATE OR REPLACE TABLE joined_data AS
SELECT
    p.Area_territoriale,
    p.Regione,
    p.Prov,
    p.Comune_ISTAT,
    p.Comune_cat,
    p.Sez,
    p.Comune_amm,
    p.Comune_descrizione,
    p.Fascia,
    p.Zona,
    p.LinkZona,
    p.Cod_Tip,
    p.Descr_Tipologia,
    p.Stato,
    p.Stato_prev,
    p.Compr_min,
    p.Compr_max,
    p.Sup_NL_compr,
    p.Loc_min,
    p.Loc_max,
    p.Sup_NL_loc,
    p.column21,
    l.Zona_Descr,
    l.Cod_tip_prev,
    l.Descr_tip_prev,
    l.Stato_prev AS Stato_prev_luoghi,
    l.Microzona,
    l.column16
FROM
    prezzi AS p
LEFT JOIN
    luoghi AS l
ON
    p.Area_territoriale = l.Area_territoriale AND
    p.Regione = l.Regione AND
    p.Prov = l.Prov AND
    p.Comune_ISTAT = l.Comune_ISTAT AND
    p.Comune_cat = l.Comune_cat AND
    p.Sez = l.Sez AND
    p.Comune_amm = l.Comune_amm AND
    p.Comune_descrizione = l.Comune_descrizione AND
    p.Fascia = l.Fascia AND
    p.Zona = l.Zona AND
    p.LinkZona = l.LinkZona;
    """
    conn.sql(create_prezzi_statement)
    conn.sql(create_luoghi_statement)
    conn.sql(create_joined_data_statement)
