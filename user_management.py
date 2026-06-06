import streamlit as st
import psycopg2
from db_config import DB_CONFIG

st.markdown("""
<style>

/* Main Background */
           

.stApp {
    background: linear-gradient(
        135deg,
        #064e3b 0%,
        #059669 50%,
        #34d399 100%
    );
}

/* Input boxes */
.stTextInput > div > div > input {
    border-radius: 10px;
    padding: 10px;
}

/* Login Button */
.stButton > button {
    width: 100%;
    border-radius: 13px;
    height: 30px;
    font-size: 18px;
    font-weight: bold;
}

/* Hide Streamlit Menu */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)


def login():

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        # st.markdown("###🎯 Order Control Center")

        
        st.markdown(
    "<h1 style='text-align:center;'>🎯 Order Control Center</h1>",
    unsafe_allow_html=True
)
        


        # st.markdown("### Login")

        with st.container(border=True):

            username = st.text_input(
                "👤 Username",
                placeholder="Enter username"
            )

            password = st.text_input(
                "🔑 Password",
                type="password",
                placeholder="Enter password"
            )

            if st.button(
                "Login",
                use_container_width=True,
                type="primary"
            ):

                try:
                    conn = psycopg2.connect(**DB_CONFIG)
                    cur = conn.cursor()

                    cur.execute(
                        """
                        SELECT
                            id,
                            username,
                            password_hash,
                            role
                        FROM users_list
                        WHERE username=%s
                        """,
                        (username,)
                    )

                    user = cur.fetchone()

                    cur.close()
                    conn.close()

                    if user:

                        if password == user[2]:

                            st.session_state.logged_in = True
                            st.session_state.user_id = user[0]
                            st.session_state.username = user[1]
                            st.session_state.role = user[3]

                            st.rerun()

                        else:
                            st.error("❌ Invalid Password")

                    else:
                        st.warning("⚠️ User Not Found")

                except Exception as e:
                    st.error(f"Error: {e}")
# def login():

#     st.title("🔐 Login")

#     username = st.text_input("Username")
#     password = st.text_input("Password", type="password")

#     if st.button("Login"):

#         try:
#             conn = psycopg2.connect(**DB_CONFIG)
#             cur = conn.cursor()

#             cur.execute(
#                 """
#                 SELECT
#                     id,
#                     username,
#                     password_hash,
#                     role
#                 FROM users_list
#                 WHERE username = %s
#                 """,
#                 (username,)
#             )

#             user = cur.fetchone()

#             cur.close()
#             conn.close()

#             if user:

#                 db_password = user[2]

#                 if password == db_password:

#                     st.session_state.logged_in = True
#                     st.session_state.user_id = user[0]
#                     st.session_state.username = user[1]
#                     st.session_state.role = user[3]

#                     st.rerun()

#                 else:
#                     st.error("Invalid Password")

#             else:
#                 st.error("User Not Found")

#         except Exception as e:
#             st.error(f"Error: {e}")

def create_user():

    menu = st.radio(
        "User Management",
        ["Create User", "View Users"]
    )

    if menu == "Create User":

        st.subheader("Create User")

        username = st.text_input("New Username")
        password = st.text_input("New Password", type="password")

        role = st.selectbox(
            "Role",
            ["user", "admin"]
        )

        if st.button("Create User"):

            try:
                conn = psycopg2.connect(**DB_CONFIG)
                cur = conn.cursor()

                cur.execute(
                    """
                    SELECT 1
                    FROM users_list
                    WHERE username = %s
                    """,
                    (username,)
                )

                if cur.fetchone():
                    st.error("Username already exists")

                else:

                    cur.execute(
                        """
                        INSERT INTO users_list
                        (
                            username,
                            password_hash,
                            role
                        )
                        VALUES
                        (
                            %s,
                            %s,
                            %s
                        )
                        """,
                        (username, password, role)
                    )

                    conn.commit()

                    st.success("User Created Successfully")

                cur.close()
                conn.close()

            except Exception as e:
                st.error(f"Error: {e}")

    elif menu == "View Users":

        try:
            conn = psycopg2.connect(**DB_CONFIG)

            query = """
            SELECT
                id,
                username,
                role,
                created_at
            FROM users_list
            ORDER BY id
            """

            import pandas as pd

            df = pd.read_sql(query, conn)

            st.subheader("User List")
            st.dataframe(df, use_container_width=True)

            conn.close()

        except Exception as e:
            st.error(f"Error: {e}")




# def create_user():

#     st.subheader("Create User")

#     username = st.text_input("New Username")
#     password = st.text_input("New Password", type="password")

#     role = st.selectbox(
#         "Role",
#         ["user", "admin"]
#     )

#     if st.button("Create User"):

#         try:
#             conn = psycopg2.connect(**DB_CONFIG)
#             cur = conn.cursor()

#             cur.execute(
#                 """
#                 SELECT 1
#                 FROM users_list
#                 WHERE username = %s
#                 """,
#                 (username,)
#             )

#             if cur.fetchone():

#                 st.error("Username already exists")

#             else:

#                 cur.execute(
#                     """
#                     INSERT INTO users_list
#                     (
#                         username,
#                         password_hash,
#                         role
#                     )
#                     VALUES
#                     (
#                         %s,
#                         %s,
#                         %s
#                     )
#                     """,
#                     (username, password, role)
#                 )

#                 conn.commit()

#                 st.success("User Created Successfully")

#             cur.close()
#             conn.close()

#         except Exception as e:
#             st.error(f"Error: {e}")

