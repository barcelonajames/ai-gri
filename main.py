"""
main.py
Entry point and page routing for Ai-gri.
Run with: streamlit run main.py
"""

import streamlit as st
from db import init_db
from login import show_login
from register import show_register
from dashboard import show_dashboard

st.set_page_config(page_title="Ai-gri", page_icon="🌾", layout="wide")

init_db()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "farmer" not in st.session_state:
    st.session_state.farmer = None
if "page" not in st.session_state:
    st.session_state.page = "login"


def main():
    if st.session_state.logged_in and st.session_state.farmer:
        show_dashboard(st.session_state.farmer)
    elif st.session_state.page == "register":
        show_register()
    else:
        show_login()


if __name__ == "__main__":
    main()
