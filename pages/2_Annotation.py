'''
TREC correction app - page 1
This page aims to annotate images with correct number labels
'''
import numpy as np
import streamlit as st
import img_display
import sidebar
import train

sidebar.sidebar_progress()

if 'uploaded_file_name' in st.session_state:
    st.write(f"Fichier analysé : {repr(st.session_state['uploaded_file_name'])}")

annot_type = st.radio(
        "Comment annoter les symboles :",
        ["Monolabel", "Plusieurs labels"],
        captions=["La feuille contient un seul type de symbole", "La feuille contient différents symboles"],
        key="label-type")
if annot_type == "Monolabel":
    with st.form("monolabel-annot"):
        st.number_input('Label', key="label-value", min_value=0, max_value=9, step=1)
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.session_state['annot_labels'] = np.full(200, st.session_state['label-value'])
            st.write("Monolabel, valeur :", st.session_state['label-value'])

if 'roi_symbols' not in st.session_state:
    st.write("Veuillez d'abord extraire les symboles")
else:
    with st.expander("Voir/Cacher les symboles extraits"):
        excluded_index = []
        controls = st.columns(3)
        with controls[0]:
            label = st.radio("Tri par label :", ["Vide", "Numéros", "Annotations"], key='label-sorting2')
            if label == "Vide":
                labels_fig = st.session_state['blank_labels']
            elif label == "Numéros":
                labels_fig = st.session_state['sheet_labels']
            elif label == "Annotations":
                labels_fig = st.session_state['annot_labels']
        with controls[1]:
            size_match = {20: "Petit", 12: "Moyen", 6: "Grand"}
            row_size = st.select_slider("Taille:", [20, 12, 6], format_func=lambda x: size_match[x], value=12,
                                        key='row-size-annot')
        with controls[2]:
            exclude_exemple = st.checkbox("Exclure les cases exemple", key='exclude-exemple')
            if exclude_exemple:
                excluded_index = range(9)
        img_display.roi_display(st.session_state['roi_symbols'], labels_fig, row_size, excluded_index)

if 'annot_labels' in st.session_state:
    keeper_index = [i for i in range(0, 200) if i not in excluded_index]
    d = train.Dataset(st.session_state['roi_symbols'][keeper_index], st.session_state['annot_labels'][keeper_index])
    st.write(d.dataset.shape)
    file_name = st.session_state["uploaded_file_name"].split('.')[0]
    st.download_button(
        label="Download .csv dataset",
        data=d.convert_csv(),
        file_name=f'{file_name}.csv',
        mime="text/csv"
    )

st.write(st.session_state)