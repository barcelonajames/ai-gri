"""
login.py
Login page for FarmAI.
"""

import streamlit as st
from db import login_user


def show_login():
    left, center, right = st.columns([1, 2, 1])

    with center:
        st.title("🌾 Ai-gri")
        st.caption("Login to your farm dashboard")

        with st.container(border=True):
            username = st.text_input("Username", key="login_username")
            password = st.text_input(
                "Password", type="password", key="login_password"
            )

            if st.button("Login", type="primary", use_container_width=True):
                if not username or not password:
                    st.error("Please enter both username and password.")
                else:
                    farmer = login_user(username, password)
                    if farmer:
                        st.session_state.logged_in = True
                        st.session_state.farmer = farmer
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")

        st.write("")
        c1, c2 = st.columns([3, 1])
        with c1:
            st.caption("Don't have an account yet?")
        with c2:
            if st.button("Register", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()
