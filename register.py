"""
register.py
Registration page for FarmAI.
"""

import streamlit as st
from db import register_user


def show_register():
    left, center, right = st.columns([1, 2, 1])

    with center:
        st.title("Create your FarmAI account")

        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                first_name = st.text_input("First name")
            with c2:
                last_name = st.text_input("Last name")

            username = st.text_input("Username")
            password = st.text_input(
                "Password", type="password", help="At least 6 characters"
            )
            confirm_password = st.text_input(
                "Confirm password", type="password"
            )

            if st.button("Register", type="primary", use_container_width=True):
                if password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, msg = register_user(
                        username, password, first_name, last_name
                    )
                    if success:
                        st.success(msg + " You can now log in.")
                        st.session_state.page = "login"
                        st.rerun()
                    else:
                        st.error(msg)

        st.write("")
        c1, c2 = st.columns([3, 1])
        with c1:
            st.caption("Already have an account?")
        with c2:
            if st.button("Login", use_container_width=True):
                st.session_state.page = "login"
                st.rerun()
