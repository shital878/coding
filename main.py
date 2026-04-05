import streamlit as st
from masala_master import masala_master
from outlet_onboarding import outlet_onaboard   # ← missing import
from order_details import order_details 
from record import records

st.sidebar.title("Product Order System")

menu = st.sidebar.radio(
    "Menu",
    ["Product Master", "Outlet Onboard", "Order Master","Records"]
)

if menu == "Product Master":
    masala_master()

elif menu == "Outlet Onboard":
    outlet_onaboard()

elif menu == "Order Master":
    order_details()

elif menu == "Records":
    records()
