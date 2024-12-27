#!/usr/bin/env python3
import os
import streamlit as st
import json
import streamlit_folium as st_folium
import folium
import geopandas as gpd

@st.cache_data
def load_geodataframe(file_path):
    return gpd.read_file(file_path)

dirname = os.path.dirname(os.path.abspath(__file__))
regions_filename = os.path.join(dirname, 'data', 'geojsons', 'limits_IT_regions.geojson')
provinces_filename = os.path.join(dirname, 'data', 'geojsons', 'limits_IT_provinces.geojson')
municipalities_filename = os.path.join(dirname, 'data', 'geojsons', 'limits_IT_municipalities.geojson')

def create_map(data_gdf, highlight_column, callback_column, callback_key):
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

        # Optionally, add a marker at the center of the geometry
        folium.Marker(
            location=[row["geometry"].centroid.y, row["geometry"].centroid.x],
            popup=f"<b>{row[highlight_column]}</b>"
        ).add_to(m)

    return m

def map_tab(conn):
    st.title("Italian Real Estate Prices")
    st.caption("Downloaded from Agenzia delle Entrate - current data is from 1st semester 2024")

    if "level" not in st.session_state:
        st.session_state.level = "region"
    if "selected_region" not in st.session_state:
        st.session_state.selected_region = None
    if "selected_province" not in st.session_state:
        st.session_state.selected_province = None

    regions_gdf = load_geodataframe(regions_filename)
    provinces_gdf = load_geodataframe(provinces_filename)
    municipalities_gdf = load_geodataframe(municipalities_filename)    

    if st.session_state.level == "region":
        st.write("### Select a Region")
        m = create_map(regions_gdf, "reg_name", "reg_istat_code", "selected_region")
        output = st_folium.folium_static(m, height=600)

        # Debugging: Check the entire output structure
        st.write("Map Output:", output)

        # Check if the map interaction has updated the session state
        if output and "last_clicked" in output:
            clicked_properties = output["last_clicked"].get("properties", {})
            st.write("Clicked Properties:", clicked_properties)  # Debugging: Check clicked properties

            if "reg_istat_code" in clicked_properties:
                st.session_state.selected_region = clicked_properties["reg_istat_code"]
                st.session_state.level = "province"
                st.write(f"Transitioning to province level with region: {st.session_state.selected_region}")
            else:
                st.write("No region code found in clicked properties.")

    elif st.session_state.level == "province":
        st.write(f"### Selected Region: {st.session_state.selected_region}")
        selected_provinces = provinces_gdf[
            provinces_gdf["reg_istat_code"] == st.session_state.selected_region
        ]
        m = create_map(selected_provinces, "prov_name", "prov_istat_code", "selected_province")
        st_folium.folium_static(m, height=600)

        # Debugging: Check if a province is selected
        st.write(f"Selected Province: {st.session_state.selected_province}")

        if st.session_state.selected_province:
            st.session_state.level = "municipality"
            st.session_state.selected_province = st.session_state.selected_province

    elif st.session_state.level == "municipality":
        st.write(f"### Selected Province: {st.session_state.selected_province}")
        selected_municipalities = municipalities_gdf[
            municipalities_gdf["prov_istat_code"] == st.session_state.selected_province
        ]
        m = create_map(
            selected_municipalities, "name", "op_id", None
        )
        st_folium.folium_static(m, height=600)

    if st.button("Reset"):
        st.session_state.level = "region"
        st.session_state.selected_region = None
        st.session_state.selected_province = None