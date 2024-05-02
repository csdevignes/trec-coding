'''
TREC correction app - page 1
This page aims to annotate images with correct number labels
'''
import streamlit as st
import img_display

if 'uploaded_file_name' in st.session_state:
    st.write(f"Fichier analysé : {repr(st.session_state['uploaded_file_name'])}")
if 'roi_symbols' not in st.session_state:
    st.write("Veuillez d'abord extraire les symboles")
else:
    with st.expander("Voir/Cacher les symboles extraits"):
        controls = st.columns(2)
        with controls[0]:
            label = st.radio("Tri par label :", ["Vide", "Numéros"], key='label-sorting2')
            if label == "Vide":
                labels_fig = st.session_state['blank_labels']
            elif label == "Numéros":
                labels_fig = st.session_state['sheet_labels']
        with controls[1]:
            row_size = st.select_slider("Row size:", range(1, 21), value=12, key='row-size-roi2')
        img_display.roi_display(st.session_state['roi_symbols'], labels_fig, row_size)

with st.form('annotation-type'):
    submitted = st.form_submit_button("Annoter")
    annot_type = st.radio(
        "Comment annoter les symboles :",
        ["Monolabel", "Plusieurs labels"],
        captions=["La feuille contient un seul type de symbole", "La feuille contient différents symboles"])
    annot_val = st.number_input('Label')
    if submitted:
        st.write(annot_type, "Valeur", annot_val)



st.write(st.session_state)