import sqlite3
import pandas as pd
import streamlit as st

conn = sqlite3.connect("training.db")

tables = pd.read_sql_query(
    """
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    """,
    conn
)

st.write("Tables disponibles :")
st.dataframe(tables)

for table in tables["name"]:

    st.write(f"### Table : `{table}`")

    structure = pd.read_sql_query(
        f"PRAGMA table_info('{table}')",
        conn
    )

    st.dataframe(structure)

conn.close() 