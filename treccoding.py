'''
Multipage version of the streamlit app
'''

import streamlit as st

st.set_page_config(
    page_title="TREC symbols correction",
    page_icon="👋",
)

st.sidebar.success("Start by extracting your symbols")

st.markdown("""# trec-coding 
Symbols classification for automatic correction for the coding part of the TREC psychometric test""")