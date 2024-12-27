#!/usr/bin/env python3

import duckdb
import streamlit as st
import geopandas as gpd
import folium
import streamlit_folium as st_folium
import os

# Set page configuration as the first Streamlit command
st.set_page_config(layout="wide", page_title="Interactive Real Estate Map", page_icon="🌍")

from init_db import init_db
from maptab import map_tab



@st.cache_data(hash_funcs={duckdb.DuckDBPyConnection: id})
def get_regions(conn):
    return conn.execute("SELECT DISTINCT Regione FROM luoghi ORDER BY Regione").df()

@st.cache_data(hash_funcs={duckdb.DuckDBPyConnection: id})
def get_municipalities(conn, region):
    return conn.execute(f"SELECT DISTINCT Comune_descrizione FROM luoghi WHERE Regione = '{region}' ORDER BY Comune_descrizione").df()

@st.cache_data
def load_geodataframe(file_path):
    return gpd.read_file(file_path)

def create_map(data_gdf, highlight_column):
    m = folium.Map(location=[42.5, 12.5], zoom_start=6, tiles="cartodbpositron")

    for _, row in data_gdf.iterrows():
        feature = folium.GeoJson(
            row["geometry"],
            name=row[highlight_column],
            tooltip=row[highlight_column],
            style_function=lambda x: {
                "fillColor": "blue",
                "color": "black",
                "weight": 1,
                "fillOpacity": 0.4,
            },
            highlight_function=lambda x: {"weight": 3, "fillOpacity": 0.7},
            popup=folium.Popup(f"<b>{row[highlight_column]}</b>", parse_html=True)
        )
        feature.add_to(m)

    return m

def main():
    """
    Main function that serves as the entry point for the application.
    """
    try:
        conn = duckdb.connect(database="dati-immobiliari.duckdb")
        init_db(conn)

        tableTab, mapTab  = st.tabs(["Table", "Map"])

        with tableTab:
            st.title("Italian Real Estate Prices")
            st.caption("Downloaded from Agenzia delle Entrate - current data is from 1st semester 2024")

            show_all_columns = st.checkbox("Show all columns", value=False)

            default_columns = {
                "Comune_descrizione": "Municipality",
                "Descr_Tipologia": "Type",
                "Zona_Descr": "Zones",
                "Compr_min": "Minimum purchase price per sqm (€)",
                "Compr_max": "Maximum purchase price per sqm (€)",
                "Loc_min": "Minimum rental price per sqm (€)",
                "Loc_max": "Maximum rental price per sqm (€)"
            }

            regions_dataset = get_regions(conn)["Regione"]
            selected_region = st.selectbox("Select a region", regions_dataset)

            if selected_region is not None:
                municipalities_dataset = get_municipalities(conn, selected_region)["Comune_descrizione"]
                selected_municipality = st.selectbox("Select a municipality", municipalities_dataset)

                if selected_municipality is not None:
                    selected_building_type = st.selectbox("Select the type of building", ("Residential buildings", "Offices", "Shops"))

                    building_types = {
                        "Residential buildings": "Abitazioni civili",
                        "Offices": "Uffici",
                        "Shops": "Negozi"
                    }

                    if selected_building_type is not None:
                        result = conn.execute(f"SELECT * FROM joined_data WHERE Regione = '{selected_region}' and Comune_descrizione = '{selected_municipality}' and Descr_Tipologia = '{building_types[selected_building_type]}'").df()
                        readable_columns = {**default_columns, **{col: col for col in result.columns if col not in default_columns}}

                        if show_all_columns:
                            st.dataframe(result)
                        else:
                            display_df = result[list(default_columns.keys())].rename(columns=default_columns)
                            st.dataframe(display_df)

        with mapTab:
            pass

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return 1

    return 0

if __name__ == "__main__":
    # This ensures the main() function only runs if the script is executed directly
    # (not when imported as a module)
    exit(main())