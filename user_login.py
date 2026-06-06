import streamlit as st
import psycopg2
from db_config import DB_CONFIG

def create_user():

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

            # Check if username already exists
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

        except Exception as e:
            st.error(f"Database Error: {e}")

        finally:
            if 'cur' in locals():
                cur.close()
            if 'conn' in locals():
                conn.close()

# create_user()