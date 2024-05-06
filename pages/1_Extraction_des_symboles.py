'''
TREC correction app - page 1
This page aims to upload file, and extract images
'''


import numpy as np
import streamlit as st
import extract
import img_display
import sidebar

sidebar.sidebar_progress()


def store_value(key):
    st.session_state[key] = st.session_state["_"+key]
def load_value(key):
    st.session_state["_"+key] = st.session_state[key]

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

    @st.experimental_fragment
    def box_extraction_process():
        b.extract_boxes()
        st.write(f"Boites extraites avec la rotation {st.session_state['rotation-degree']} : dimensions {b.box_coord.shape}")
        with st.expander("Voir/Cacher les boites détectées"):
            st.image(b.plot_boxes(b.box_coord))
        st.session_state['box_coord'] = b.box_coord
    if st.button("Détecter les boites"):
        box_extraction_process()
    start_roi_extraction = 'box_coord' in st.session_state and len(st.session_state.get('box_coord', [])) == 400

    if start_roi_extraction:
        def store_roi_symbols():
            r = extract.ROIExtract(b.img_rot)
            r.extract_roi_symbols(st.session_state['box_coord'])
            st.write(f'Symboles extraits : dimension {r.roi_symbols.shape}')
            st.session_state['roi_symbols'] = r.roi_symbols
            st.session_state['sheet_labels'] = r.sheet_labels
            st.session_state['blank_labels'] = r.blank_labels
        if st.button("Extraire les symboles"):
            store_roi_symbols()

if 'roi_symbols' in st.session_state:
    with st.expander("Voir/Cacher les symboles extraits"):
        controls = st.columns(2)
        with controls[0]:
            label_match = {'blank_labels': "Vides (zeros)",
                           'sheet_labels': "Numéros de la feuille"}
            labels_display_code = st.radio("Charger les labels :", ['blank_labels', 'sheet_labels'],
                                         format_func=lambda x: label_match[x], key="labels_display")
            labels_display = st.session_state[labels_display_code]

        with controls[1]:
            size_match = {20: "Petit", 12: "Moyen", 6: "Grand"}
            row_size = st.select_slider("Taille:", [20, 12, 6], format_func=lambda x: size_match[x], value=12, key='row-size-roi')
        img_display.roi_display(st.session_state['roi_symbols'], labels_display, row_size)

st.write(st.session_state)