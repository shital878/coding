import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime
from db_config import DB_CONFIG

def order_details():

    st.header("Order Master")

    connection = psycopg2.connect(**DB_CONFIG)
    cursor = connection.cursor()

    menu = st.sidebar.radio("Order", ["Order","Update"])
    query = "SELECT * FROM masala_master"
    df = pd.read_sql(query, connection)

    # Load Customer Master
    cust_query = "SELECT shop_name FROM customer"
    cust_df = pd.read_sql(cust_query, connection)




    # ================= ORDER PAGE =================
    if menu == "Order":

        cust_name = st.selectbox("Select Customer", cust_df["shop_name"])

        with st.form("order_form", clear_on_submit=True):

            st.subheader("Enter Order Details")

            # Table Header
            h1, h2, h3 = st.columns([1.5,1,1])
            h1.markdown("**Masala Name**")
            h2.markdown("**Qty**")
            h3.markdown("**Rate**")

            order_data = []

            for index, row in df.iterrows():

                masala_id = row["id"]
                masala_name = row["masala_name"]

                col1, col2, col3 = st.columns([1.5,1,1])

                col1.text_input(
                    "",
                    value=masala_name,
                    disabled=True,
                    key=f"name_{masala_id}"
                )

                qty = col2.number_input("", min_value=0, key=f"qty_{masala_id}")
                rate = col3.number_input("", min_value=0, key=f"rate_{masala_id}")

                amount = qty * rate

                order_data.append((masala_id, masala_name, qty, rate, amount))

            # Submit button OUTSIDE loop
            submit = st.form_submit_button("Submit Order")


        if submit:

            cursor = connection.cursor()

            inserted = False
            error_found = False

            for data in order_data:

                masala_id, masala_name, qty, rate, amount = data

                # Skip empty rows
                if qty == 0 and rate == 0:
                    continue

                # Qty validation
                if qty <= 0:
                    st.error(f"Quantity must be greater than 0 for {masala_name}")
                    error_found = True
                    continue

                # Rate validation
                if rate <= 0:
                    st.error(f"Rate must be greater than 0 for {masala_name}")
                    error_found = True
                    continue

                # Duplicate check
                check_query = """
                SELECT COUNT(*)
                FROM masala_order
                WHERE cust_name = %s
                AND masala_name = %s
                AND business_date = CURRENT_DATE
                """

                cursor.execute(check_query, (cust_name, masala_name))
                count = cursor.fetchone()[0]

                if count > 0:

                    st.warning(f"{masala_name} already ordered today")

                else:

                    insert_query = """
                    INSERT INTO masala_order
                    (id, cust_name, masala_name, qty, rate, amount, business_date, order_time)
                    VALUES (%s, %s, %s, %s, %s, %s, CURRENT_DATE, CURRENT_TIMESTAMP)
                    """

                    cursor.execute(
                        insert_query,
                        (masala_id, cust_name, masala_name, qty, rate, amount)
                    )

                    inserted = True

            if not error_found:
                connection.commit()

            if inserted:
                st.success("Order Inserted Successfully")
            else:
                st.error("Please enter valid Qty and Rate")


    # ================= UPDATE PAGE =================
    elif menu == "Update":

        st.title("Update Masala Order")

        cust_name = st.selectbox("Select Customer", cust_df["shop_name"])

        # cust_name = st.text_input("Customer Name")
        masala_name = st.selectbox("Masala Name", df["masala_name"])

        col1, col2 = st.columns(2)

        new_qty = col1.number_input("New Quantity", min_value=1)
        new_rate = col2.number_input("New Rate", min_value=1)

        if st.button("Update Order"):

            new_amount = new_qty * new_rate

            cursor = connection.cursor()

            update_query = """
            UPDATE masala_order
            SET qty = %s,
                rate = %s,
                amount = %s
            WHERE cust_name = %s
            AND masala_name = %s
            AND business_date = CURRENT_DATE
            """

            cursor.execute(update_query,
                           (new_qty, new_rate, new_amount, cust_name, masala_name))

            connection.commit()

            st.success("Order Updated Successfully")


# order_details()


