# streamlit run coding/masala_master.py
import streamlit as st
import pandas as pd
import psycopg2
from db_config import DB_CONFIG

# st.title("Masala Master System")

def masala_master():

     # ---------------- PAGE CONFIG ----------------
    # st.set_page_config(page_title="Outlet Management System", layout="wide")
    
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
    # st.markdown('<div class="main-title">Outlet Management System</div>', unsafe_allow_html=True)


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