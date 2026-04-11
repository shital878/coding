import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime
from db_config import DB_CONFIG




def outlet_onaboard():


    # ---------------- PAGE CONFIG ----------------
    st.set_page_config(page_title="Outlet Management System", layout="wide")

    # ---------------- CUSTOM CSS ----------------
    st.markdown("""
<style>

/* Main Background */

[data-testid="stAppViewContainer"]{
background: linear-gradient(to right,#d6eaf8,#f9ebea);
}

/* Center Title */

.main-title{
font-size:40px;
font-weight:bold;
text-align:center;
color:#154360;
margin-bottom:25px;
}

/* Card Design */

.card{
background:white;
padding:30px;
border-radius:12px;
box-shadow:0px 4px 12px rgba(0,0,0,0.15);
margin-bottom:20px;
}

/* Text Input */

div[data-baseweb="input"] > div{
background-color:#fdfefe;
border:2px solid #2E86C1;
border-radius:8px;
}

div[data-baseweb="input"] > div:focus-within{
border:2px solid #1B4F72;
background-color:#EBF5FB;
}

/* Labels */

label{
color:#154360 !important;
font-weight:600;
}

 /* Buttons */

.stButton > button,
div[data-testid="stFormSubmitButton"] > button{
background:#28B463;
color:white;
border-radius:8px;
height:42px;
width:200px;
font-weight:bold;
border:none;
}

/* Hover */

.stButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover{
background:#1D8348;
color:white;
}

/* Sidebar */

section[data-testid="stSidebar"]{
background-color:#F8C471;
}

</style>
""", unsafe_allow_html=True)

    # ---------------- TITLE ----------------
    st.markdown('<div class="main-title">Outlet Management System</div>', unsafe_allow_html=True)


#     # ---------------- DATABASE CONNECTION ----------------
#     connection = psycopg2.connect(
#     database="maindatabase",
#     user="avnadmin",
#     password="AVNS_qn7sCvj55GiZ2Ghq4Cz",
#     host="pg-3a0c1943-shital878-5c07.g.aivencloud.com",
#     port="18902"
# )

    # ---------------- SIDEBAR ----------------
    st.sidebar.title("Navigation")

    menu = st.sidebar.radio(
        "Menu",
        ["Outlet Registration","Update Outlet","All Outlet"]
    )

    # =====================================================
    # OUTLET REGISTRATION
    # =====================================================

    if menu == "Outlet Registration":

        st.subheader("Register New Outlet")

        with st.form("form1", clear_on_submit=True):

            col1,col2 = st.columns(2)

            with col1:
                SN = st.text_input("**Shop Name***")
                MOBILE_NO = st.text_input("**Mobile Number***")
                DISTRICT = st.text_input("**District**")

            with col2:
                WN = st.text_input("**Owner Name***")
                STATE_NAME = st.text_input("**State Name**")
                ADDRESS = st.text_input("**Address**")

            submit = st.form_submit_button("Submit")

        if submit:

            errors = []

            if SN.strip() == "":
                errors.append("Shop Name is mandatory")

            if WN.strip() == "":
                errors.append("Owner Name is mandatory")

            if MOBILE_NO.strip() == "":
                errors.append("Mobile Number is mandatory")

            # If any error exists
            if errors:
                for err in errors:
                    st.error(err)

            else:

                cursor = connection.cursor()

                check_query = """
                SELECT COUNT(*) FROM customer
                WHERE shop_name=%s AND owner_name=%s AND mobile_no=%s
                """

                cursor.execute(check_query,(SN,WN,MOBILE_NO))
                count = cursor.fetchone()[0]

                if count > 0:
                    st.error(f"{SN} Outlet Already Exists")

                else:

                    insert_query = """
                    INSERT INTO customer
                    (shop_name,owner_name,mobile_no,district,state_name,address)
                    VALUES (%s,%s,%s,%s,%s,%s)
                    """

                    cursor.execute(insert_query,(SN,WN,MOBILE_NO,DISTRICT,STATE_NAME,ADDRESS))
                    connection.commit()

                    st.success("Outlet Inserted Successfully")


    # =====================================================
    # UPDATE OUTLET
    # =====================================================

    elif menu == "Update Outlet":

        st.subheader("Update Outlet")

        col1,col2 = st.columns(2)

        cust_id = col1.number_input("**Outlet ID**", min_value=0)

        SHOP_NAME = col1.text_input("**Shop Name**")
        OWNER_NAME = col2.text_input("**Owner Name**")

        MOBILE_NO = col1.text_input("**Mobile Number**")
        DISTRICT = col1.text_input("**District**")

        STATE_NAME = col2.text_input("**State Name**")
        ADDRESS = col2.text_input("**Address**")

        if st.button("Update Outlet"):

            cursor = connection.cursor()

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
            (SHOP_NAME,OWNER_NAME,MOBILE_NO,DISTRICT,STATE_NAME,ADDRESS,cust_id))

            connection.commit()

            st.success("Outlet Updated Successfully")


    # =====================================================
    # ALL OUTLETS
    # =====================================================

    elif menu == "All Outlet":

        st.header("All Outlet List")

        query = "SELECT * FROM customer"
        df = pd.read_sql(query, connection)

        # Create two columns
        col1, col2 = st.columns(2)

        # District list
        city = df["district"].dropna().unique()
        selected_city = col1.selectbox("**Select City**", ["All"] + list(city))

        # Business Date Filter
        date_list = df["business_date"].dropna().unique()
        selected_date = col2.selectbox("**Select Business Date**", ["All"] + list(date_list))

        # Filter only if city selected
        if selected_city == "All":
            filtered_df = df
        else:
            filtered_df = df[df["district"] == selected_city]

        # Apply Date Filter
        if selected_date != "All":
            filtered_df = filtered_df[filtered_df["business_date"] == selected_date]

        st.dataframe(filtered_df, use_container_width=True, hide_index=True)




    # elif menu == "All Outlet":

    #     st.subheader("All Outlet List")

    #     query = "SELECT * FROM customer"

    #     df = pd.read_sql(query, connection)

    #     city=df["district"].unique()
    #     selected_city=st.selectbox("select city:",city)

    #     filtered_df=df[df["district"] == selected_city]

    #     st.dataframe(filtered_df, use_container_width=True)





    # elif menu == "All Outlet":

    #     st.subheader("All Outlet List")

    #     # Load only district names
    #     city_query = "SELECT DISTINCT district FROM customer ORDER BY district"
    #     city_df = pd.read_sql(city_query, connection)

    #     city_list = city_df["district"].tolist()

    #     selected_city = st.selectbox("Select City", ["Select City"] + city_list)

    #     # Show data only after selection
    #     if selected_city != "Select City":

    #         query = "SELECT * FROM customer WHERE district = %s"

    #         df = pd.read_sql(query, connection, params=[selected_city])

    #         st.dataframe(df, use_container_width=True)

# outlet_onaboard()