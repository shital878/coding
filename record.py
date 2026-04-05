import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime
from db_config import DB_CONFIG

def records():

    connection = psycopg2.connect(**DB_CONFIG)

    menu = st.sidebar.radio("Records", ["Pending Orders","Delivered Orders","All Orders"])

    # ================= Pending Orders =================
    if menu == "Pending Orders":

        st.header("Pending Orders")

        query = """
        SELECT * 
        FROM masala_order 
        WHERE status = 'Pending'
        ORDER BY business_date DESC
        """

        df = pd.read_sql(query, connection)

        st.dataframe(df, use_container_width=True)

    # ================= Delivered Orders =================
    elif menu == "Delivered Orders":

        st.header("Delivered Orders")

        # Load Customer List
        cust_query = "SELECT shop_name FROM customer"
        cust_df = pd.read_sql(cust_query, connection)

        col1, col2 = st.columns(2)

        cust_name = col1.selectbox("Select Customer", ["All"] + cust_df["shop_name"].tolist())
        business_date = col2.date_input("Select Business Date")

        query = "SELECT * FROM masala_order WHERE status = 'Done'"

        if cust_name != "All":
            query += f" AND cust_name = '{cust_name}'"

        if business_date:
            query += f" AND business_date = '{business_date}'"

        df = pd.read_sql(query, connection)

        st.dataframe(df, use_container_width=True)

    # ================= All Orders =================
    elif menu == "All Orders":

        st.header("All Orders")

        cust_query = "SELECT shop_name FROM customer"
        cust_df = pd.read_sql(cust_query, connection)

        col1, col2 = st.columns(2)

        cust_name = col1.selectbox("Select Customer", ["All"] + cust_df["shop_name"].tolist())
        business_date = col2.date_input("Select Business Date")

        query = "SELECT * FROM masala_order WHERE 1=1"

        if cust_name != "All":
            query += f" AND cust_name = '{cust_name}'"

        if business_date:
            query += f" AND business_date = '{business_date}'"

        df = pd.read_sql(query, connection)

        st.dataframe(df, use_container_width=True)


# records()