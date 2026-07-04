"""
login.py
Sign In page for AI-gri.
"""

import streamlit as st
from db import login_user
from theme import inject_theme, logo_centered, theme_toggle


def show_login():
    inject_theme()
    theme_toggle(where="corner")

    left, center, right = st.columns([1, 2, 1])

    with center:
        logo_centered(width=160)
        st.markdown(
            "<h2 style='text-align:center;'>Welcome back</h2>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='text-align:center;' class='sub'>"
            "Sign in to your farm dashboard</p>",
            unsafe_allow_html=True,
        )

        with st.container(border=True):
            username = st.text_input("Username", key="login_username")
            password = st.text_input(
                "Password", type="password", key="login_password"
            )

            if st.button("Sign In", type="primary", use_container_width=True):
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
            st.caption("New farmer?")
        with c2:
            if st.button("Create an account", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()
