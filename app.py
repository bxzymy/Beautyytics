import streamlit as st
from home_page import show_home_page
from analysis_page import show_analysis_page, init_session_state
from dotenv import load_dotenv
import os


def main():
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    if 'lang' not in st.session_state:
        st.session_state.lang = 'zh'

    if st.session_state.page == 'home':
        show_home_page()
    elif st.session_state.page == 'analysis':
        init_session_state()
        show_analysis_page()

if __name__ == "__main__":
    main()