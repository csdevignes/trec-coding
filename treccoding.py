'''
Multipage version of the streamlit app
'''

import streamlit as st
import sidebar

st.set_page_config(
    page_title="TREC symbols correction",
    page_icon="👋",
)


sidebar.sidebar_progress()

st.markdown("""# trec-coding 
Classification des symboles pour la correction du test de codage du TREC""")