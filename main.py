import streamlit as st
from masala_master import masala_master
from outlet_onboarding import outlet_onaboard   # ← missing import

st.sidebar.title("Product Order System")

menu = st.sidebar.radio(
    "Menu",
    ["Product Master", "Outlet Onboard", "Order Master"]
)

if menu == "Product Master":
    masala_master()

elif menu == "Outlet Onboard":
    outlet_onaboard()

elif menu == "Order Master":
    st.title("Order Master Module")