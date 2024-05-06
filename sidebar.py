'''
Multipage version of the streamlit app - Sidebar code
'''
import numpy as np
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

def sidebar_legend():
    legend = np.loadtxt("data_resultsheets/legend_pictures.csv", delimiter=',')
    leg_pict, leg_label = np.split(legend, [19740], axis=1)
    leg_pict = leg_pict.reshape((len(leg_pict), 141, 140))
    leg_pict = leg_pict / 255
    col1, col2, col3 = st.sidebar.columns([0.33, 0.33, 0.33], gap="small")
    pattern = [col1, col2, col3]
    col_list= [pattern[i % len(pattern)] for i in range(len(leg_pict))]
    for i, col in zip(range(len(leg_pict)), col_list):
        with col:
            col.image(leg_pict[i])
            # st.header(int(leg_label[i]))
            st.markdown(
                f"<p style='position:relative; top:-20px; color:red; font-size:1.5em;padding:10px;margin:0;text-align:center;'>{leg_label[i]}</p>",
                unsafe_allow_html=True)