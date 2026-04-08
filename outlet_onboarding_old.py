import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime
from db_config import DB_CONFIG

# st.title("Outlet Registration")

def outlet_onaboard():

    st.header("Outlet Master")

    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()

    menu = st.sidebar.radio("Master Menu", ["Outlet", "Update Outlet","View Outlet Data"])

    # ================= Outlet Registration =================
    if menu == "Outlet":

        st.subheader("Outlet Registration")

        with st.form("form1", clear_on_submit=True):

            col1, col2 = st.columns(2)

            SHOP_NAME = col1.text_input("SHOP_NAME")
            OWNER_NAME = col2.text_input("OWNER_NAME")
            MOBILE_NO = col1.text_input("MOBILE_NO")
            DISTRICT = col1.text_input("DISTRICT")
            STATE_NAME = col2.text_input("STATE_NAME")
            ADDRESS = col2.text_input("ADDRESS")

            submit = st.form_submit_button("Submit")

        if submit:

            check_query = """
            SELECT COUNT(*)
            FROM CUSTOMER
            WHERE SHOP_NAME = %s
            AND OWNER_NAME = %s
            AND MOBILE_NO = %s
            """

            cursor.execute(check_query, (SHOP_NAME, OWNER_NAME, MOBILE_NO))
            count = cursor.fetchone()[0]

            if count > 0:

                st.error("Outlet already loaded.")

            else:

                insert_query = """
                INSERT INTO CUSTOMER
                (SHOP_NAME, OWNER_NAME, MOBILE_NO, DISTRICT, STATE_NAME, ADDRESS)
                VALUES (%s, %s, %s, %s, %s, %s)
                """

                cursor.execute(insert_query,
                               (SHOP_NAME, OWNER_NAME, MOBILE_NO, DISTRICT, STATE_NAME, ADDRESS))

                connection.commit()

                st.success("Outlet Inserted Successfully")

    elif menu == "Update Outlet":

        st.title("Update Outlet Details")

        col1, col2 = st.columns(2)

        cust_id = col1.number_input("Enter Outlet ID", min_value=1)

        SHOP_NAME = col1.text_input("SHOP_NAME")
        OWNER_NAME = col2.text_input("OWNER_NAME")
        MOBILE_NO = col1.text_input("MOBILE_NO")
        DISTRICT = col1.text_input("DISTRICT")
        STATE_NAME = col2.text_input("STATE_NAME")
        ADDRESS = col2.text_input("ADDRESS")

        if st.button("Update Outlet"):

            # cursor = connection.cursor()
            update_query = """
UPDATE customer
SET shop_name  = COALESCE(NULLIF(%s,''), shop_name),
    owner_name = COALESCE(NULLIF(%s,''), owner_name),
    mobile_no  = COALESCE(NULLIF(%s,''), mobile_no),
    district   = COALESCE(NULLIF(%s,''), district),
    state_name = COALESCE(NULLIF(%s,''), state_name),
    address    = COALESCE(NULLIF(%s,''), address)
WHERE id = %s
"""
 

            cursor.execute(update_query,
                           (SHOP_NAME, OWNER_NAME, MOBILE_NO, DISTRICT, STATE_NAME, ADDRESS, cust_id))

            connection.commit()

            st.success("Outlet Updated Successfully")

    elif menu == "View Outlet Data":

        query = "SELECT * FROM CUSTOMER"
        df = pd.read_sql(query, connection)

        st.dataframe(df)

# Call function outside
# outlet_onaboard()