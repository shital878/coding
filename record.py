import streamlit as st
import pandas as pd
import psycopg2
from datetime import datetime
from db_config import DB_CONFIG

def records():

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


    connection = psycopg2.connect(**DB_CONFIG)

    menu = st.sidebar.radio("Records", ["All Orders"])

    

    # ================= All Orders =================
    if menu == "All Orders":

        st.header("All Orders")

        cust_query = "SELECT * FROM customer"
        cust_df = pd.read_sql(cust_query, connection)

        date_query = "SELECT distinct business_date FROM masala_order"
        date_query_df = pd.read_sql(date_query, connection)

        status = "SELECT distinct status FROM masala_order"
        status_df = pd.read_sql(status, connection)

        col1, col2 ,col3 = st.columns(3)

        cust_name = col1.selectbox("Select Customer", ["All"] + cust_df["shop_name"].tolist())

        business_date=col2.selectbox("Select Date", ["All"] + date_query_df["business_date"].tolist())
        # business_date = col2.date_input("Select Business Date")

        status = col3.selectbox("Select Status", ["All"] + status_df["status"].tolist())

        query = "SELECT * FROM masala_order WHERE 1=1"

        if cust_name != "All":
            query += f" AND cust_name = '{cust_name}'"

        if business_date != "All":
            query += f" AND business_date = '{business_date}'"


        if status !="All":
            query+=f" and status = '{status}'"

        df = pd.read_sql(query, connection)

        st.dataframe(df, use_container_width=True)





# records()