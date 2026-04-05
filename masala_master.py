# streamlit run coding/masala_master.py
import streamlit as st
import pandas as pd
import psycopg2
from db_config import DB_CONFIG

# st.title("Masala Master System")

def masala_master():

    st.header("Product Master")

    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()

    menu = st.sidebar.radio(
        "Master Menu",
        ["Insert Product", "View Product Data"]
    )

    if menu == "Insert Product":

        masala_name = st.text_input("Enter Product Name")

        if st.button("Save"):

            query = "INSERT INTO masala_master (masala_name) VALUES (%s)"
            cursor.execute(query, (masala_name,))
            connection.commit()

            st.success("Product inserted successfully")

    elif menu == "View Product Data":

        query = "SELECT * FROM masala_master"
        df = pd.read_sql(query, connection)

        st.dataframe(df)


# masala_master()
# data = masala_master()
# st.dataframe(data)