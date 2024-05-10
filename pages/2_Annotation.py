'''
TREC correction app - page 2
This page aims to annotate images with correct number labels
'''
import numpy as np
import streamlit as st
import sidebar
import train

sidebar.sidebar_progress()
sidebar.sidebar_legend()

if 'uploaded_file_name' in st.session_state:
    st.write(f"Fichier analysé : {repr(st.session_state['uploaded_file_name'])}")
if 'ex_roi_symbols' not in st.session_state:
    st.write("Veuillez d'abord extraire les symboles")

else:
    if 'annot_labels' not in st.session_state:
        st.session_state['annot_labels'] = st.session_state['sheet_labels'].copy()


# Saving dataset
if 'annot_labels' in st.session_state:
    keeper_index = [i for i in range(0, 200) if i not in an_excluded_index]
    d = train.Dataset(st.session_state['ex_roi_symbols'][keeper_index], st.session_state['annot_labels'][keeper_index])
    st.write(d.dataset.shape)
    file_name = st.session_state["uploaded_file_name"].split('.')[0]
    st.download_button(
        label="Download .csv dataset",
        data=d.convert_csv(),
        file_name=f'{file_name}.csv',
        mime="text/csv"
    )

st.write(st.session_state)