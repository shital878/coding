import streamlit as st
from masala_master import masala_master
from outlet_onboarding import outlet_onaboard
from order import order_details
from record import records
from user_management import login, create_user




# Session Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "role" not in st.session_state:
    st.session_state.role = None
    # st.session_state.role = None

if "username" not in st.session_state:
    st.session_state.username = None


# ==========================
# SHOW LOGIN PAGE ONLY
# ==========================

if not st.session_state.logged_in:

    login()
 

    # IMPORTANT
    st.stop()


# ==========================
# AFTER LOGIN ONLY
# ==========================

st.sidebar.success(
    f"Welcome {st.session_state.username}"
)

st.sidebar.write(
    f"Role : {st.session_state.role}"
)

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()

menu_list = [
    "Product Master",
    "Outlet Onboard",
    "Order Master",
    "Records"
]

if st.session_state.role == "admin":
    menu_list.append("User Management")

st.sidebar.title("Product Order System")

menu = st.sidebar.radio(
    "Menu",
    menu_list
)

if menu == "Product Master":
    masala_master()

elif menu == "Outlet Onboard":
    outlet_onaboard()

elif menu == "Order Master":
    order_details()

elif menu == "Records":
    records()

elif menu == "User Management":
    create_user()

