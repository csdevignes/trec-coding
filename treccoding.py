'''
Multipage version of the streamlit app
'''

import streamlit as st

st.set_page_config(
    page_title="TREC symbols correction",
    page_icon="👋",
)

if 'uploaded_file_name' in st.session_state:
    st.sidebar.success(f"Fichier analysé : {repr(st.session_state['uploaded_file_name'])}")
else:
    st.sidebar.success("Start by extracting your symbols")
if 'roi_symbols' in st.session_state:
    st.sidebar.success(f"Symboles extraits : {len(st.session_state['roi_symbols'])}")

st.markdown("""# trec-coding 
Symbols classification for automatic correction for the coding part of the TREC psychometric test""")