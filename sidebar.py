'''
Multipage version of the streamlit app - Sidebar code
'''

import streamlit as st

def sidebar_progress():
    if 'uploaded_file_name' in st.session_state:
        st.sidebar.success(f"Fichier analysé : {repr(st.session_state['uploaded_file_name'])}")
    else:
        st.sidebar.success("Start by extracting your symbols")
    if 'roi_symbols' in st.session_state:
        st.sidebar.success(f"Symboles extraits : {len(st.session_state['roi_symbols'])}")
    if 'annot_labels' in st.session_state:
        st.sidebar.success('Symboles annotés')