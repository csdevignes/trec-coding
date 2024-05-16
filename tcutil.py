'''
Multipage version of the streamlit app - Common functions
'''
import numpy as np
import streamlit as st

def initialize_session(key):
    if key not in st.session_state:
        st.session_state[key] = None
def set_labels():
    '''
    Define default labels usable for all result sheet.
    '''
    st.session_state['blank_labels'] = np.zeros(200, dtype=int)
    st.session_state['sheet_labels'] = np.array([3, 6, 4, 2, 9, 8, 7, 9, 1, 6, 3, 7, 6, 2, 5, 8, 4, 1, 9, 5,
                                  2, 9, 6, 8, 1, 7, 5, 3, 4, 7, 2, 5, 3, 1, 9, 6, 7, 8, 2, 4,
                                  6, 3, 7, 9, 5, 4, 8, 1, 2, 9, 8, 4, 1, 8, 7, 5, 9, 2, 6, 3,
                                  1, 8, 5, 2, 4, 3, 9, 6, 7, 1, 5, 6, 7, 5, 1, 3, 4, 9, 8, 2,
                                  9, 7, 4, 6, 8, 2, 1, 5, 3, 2, 9, 8, 4, 3, 6, 7, 2, 5, 9, 1,
                                  4, 6, 1, 5, 3, 9, 2, 7, 8, 5, 6, 3, 9, 4, 5, 2, 6, 7, 1, 8,
                                  5, 2, 8, 1, 7, 6, 3, 4, 9, 8, 1, 2, 6, 9, 8, 1, 5, 3, 4, 7,
                                  3, 5, 2, 4, 9, 1, 7, 8, 6, 4, 3, 1, 8, 7, 2, 4, 3, 6, 5, 9,
                                  7, 1, 9, 3, 6, 8, 4, 2, 5, 6, 7, 9, 2, 6, 3, 8, 1, 4, 7, 5,
                                  8, 4, 3, 7, 2, 5, 6, 9, 1, 3, 4, 7, 5, 2, 4, 9, 8, 1, 3, 6])
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

def exclude_example(prefix):
    st.checkbox("Exclure les cases exemple", key=f'{prefix}_exclude-exemple', value=True)
    if st.session_state[f'{prefix}_exclude-exemple'] == True:
        excluded_index = range(9)
    else:
        excluded_index = []
    st.session_state[f'{prefix}_keeper_indx'] = [i for i in range(0, 200) if i not in excluded_index]
