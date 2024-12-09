#!/usr/bin/env python3

import duckdb
import streamlit as st
from init_db import init_db

@st.cache_data(hash_funcs={duckdb.DuckDBPyConnection: id})
def get_regioni(conn):
    return conn.execute("SELECT DISTINCT Regione FROM luoghi order by Regione").df()

@st.cache_data(hash_funcs={duckdb.DuckDBPyConnection: id})
def get_comuni(conn, regione):
    return conn.execute(f"SELECT DISTINCT Comune_descrizione FROM luoghi WHERE Regione = '{regione}' order by Comune_descrizione").df()


def main():
    """
    Main function that serves as the entry point for the application.
    """
    try:
        conn = duckdb.connect(database = "dati-immobiliari.duckdb")
        init_db(conn)
        
        st.set_page_config(layout="wide")
        
        st.title("Dati immobiliari Agenzia delle Entrate")
        st.caption("Dati del 2024")

        
        show_all_columns = st.checkbox("Mostra tutte le colonne", value=False)

        default_columns = {
            "Comune_descrizione" : "Comune",
            "Descr_Tipologia" : "Tipologia",
            "Zona_Descr" : "Zona",
            "Compr_min" : "Prezzo acquisto minimo al mq (€)",
            "Compr_max" : "Prezzo acquisto massimo al mq (€)",
            "Loc_min" : "Prezzo locazione minimo al mq (€)",
            "Loc_max" : "Prezzo locazione massimo al mq (€)"
        }

        regioni_dataset = get_regioni(conn)["Regione"]
        selected_regione =st.selectbox("Seleziona la regione", regioni_dataset)

        if(selected_regione != None):
            comuni_dataset = get_comuni(conn, selected_regione)["Comune_descrizione"]
            selected_comune = st.selectbox("Seleziona il comune", comuni_dataset)

            if(selected_comune != None):

                selected_tipologia = st.selectbox("Seleziona la tipologia", ("Abitazioni civili", "Uffici", "Negozi"))

                if(selected_tipologia != None):
                    result = conn.execute(f"SELECT * FROM joined_data WHERE Regione = '{selected_regione}' and Comune_descrizione = '{selected_comune}' and Descr_Tipologia = '{selected_tipologia}'").df()
                    readable_columns = {**default_columns, **{col: col for col in result.columns if col not in default_columns}}

                    if(show_all_columns):
                        st.dataframe(result)
                        
                    else:
                        
                        display_df = result[list(default_columns.keys())].rename(columns=default_columns)
                        st.dataframe(display_df)
                    
    except Exception as e:
        print(f"An error occurred: {e}")
        return 1

    return 0

if __name__ == "__main__":
    # This ensures the main() function only runs if the script is executed directly
    # (not when imported as a module)
    exit(main())