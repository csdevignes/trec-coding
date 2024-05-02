'''
TREC correction app - page 1
This page aims to upload file, and extract images
'''

# TODO: replace checkbox with toggle

import numpy as np
import streamlit as st
import extract
import img_display


def store_value(key):
    st.session_state[key] = st.session_state["_"+key]
def load_value(key):
    st.session_state["_"+key] = st.session_state[key]

# Upload custom file
uploaded_file = st.file_uploader("Upload feuille de résultat (format png)", type=['png'])
if uploaded_file is not None:
    st.session_state['uploaded_file_name'] = uploaded_file.name
    bytes_data = uploaded_file.read()
    nparr = np.frombuffer(bytes_data, np.uint8)
    b = extract.Boxdetection(nparr)
    if "rotation-degree" not in st.session_state:
        st.session_state["rotation-degree"] = 0
    load_value("rotation-degree")
    st.number_input('Degrés de rotation', min_value=-360., max_value=360.,
                             step=0.01, key="_rotation-degree", on_change=store_value,
                             args=["rotation-degree"],
                             help="Ajustez la rotation pour aligner la grille avec les lignes")

    b.image_rotation(st.session_state["rotation-degree"])
    col1, col2 = st.columns([0.5, 0.5], gap="small")
    with col1:
        st.image(b.plot_scan(b.img))
    with col2:
        st.image(b.plot_scan(b.img_rot))

    start_box_extraction = st.checkbox('Extraire les coordonnées des boites', key='start-box-extraction',
                                   help='Une fois les coordonnées enregistrées, déselectionner.')

    if start_box_extraction:
        b.extract_boxes()
        st.write(f"Boites extraites avec la rotation {st.session_state['rotation-degree']} : dimensions {b.box_coord.shape}")
        with st.expander("Voir/Cacher les boites détectées"):
            st.image(b.plot_boxes(b.box_coord))
        def store_box_coord():
            st.session_state['box_coord'] = b.box_coord
        if st.button("Enregistrer les coordonnées des boîtes"):
                store_box_coord()

    start_roi_extraction_disabled = 'box_coord' not in st.session_state or len(st.session_state.get('box_coord', [])) != 400


    start_roi_extraction = st.checkbox('Extraire les images des symboles', key='start-roi-extraction',
                                       help="Enregistrez d'abord les coordonnées",
                                       disabled=start_roi_extraction_disabled)

    if start_roi_extraction:
        r = extract.ROIExtract(b.img_rot)
        r.extract_roi_symbols(st.session_state['box_coord'])
        st.write(f'Symboles extraits : dimension {r.roi_symbols.shape}')
        with st.expander("Voir/Cacher les symboles extraits"):
            controls = st.columns(2)
            with controls[0]:
                label = st.radio("Tri par label :", ["Vide", "Numéros"], key='label-sorting')
                if label == "Vide":
                    labels_fig = r.blank_labels
                elif label == "Numéros":
                    labels_fig = r.sheet_labels
            with controls[1]:
                row_size = st.select_slider("Row size:", range(1, 21), value=12, key='row-size-roi')
            img_display.roi_display(r.roi_symbols, labels_fig, row_size)
        def store_roi_symbols():
            st.session_state['roi_symbols'] = r.roi_symbols
            st.session_state['sheet_labels'] = r.sheet_labels
            st.session_state['blank_labels'] = r.blank_labels
        # Ajouter un bouton pour enregistrer les symboles ROI
        if st.button("Enregistrer les symboles"):
            store_roi_symbols()

if 'uploaded_file_name' in st.session_state:
    st.write(f"Fichier analysé : {repr(st.session_state['uploaded_file_name'])}")

if 'roi_symbols' in st.session_state:
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

st.write(st.session_state)