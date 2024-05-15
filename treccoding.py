'''
Multipage version of the streamlit app
'''

import streamlit as st
import extract
import img_display
import sidebar
import numpy as np

st.set_page_config(
    page_title="TREC symbols correction",
    page_icon="👋",
)


sidebar.sidebar_progress()

st.markdown("""# trec-coding 
Classification des symboles pour la correction du test de codage du TREC""")

# Loading and rotating scan
if st.toggle("Prendre une photo"):
    uploaded_file = st.camera_input("Photo de la feuille de résultat")
else:
    uploaded_file = st.file_uploader("Upload feuille de résultat (format png)", type=['png'])
if uploaded_file is not None:
    st.session_state['uploaded_file_name'] = uploaded_file.name
    bytes_data = uploaded_file.read()
    nparr = np.frombuffer(bytes_data, np.uint8)
    b = extract.Boxdetection(nparr)
    st.number_input('Degrés de rotation', min_value=-360., max_value=360.,
                             step=0.01, value=0., key="ex_rotation-degree",
                             help="Ajustez la rotation pour aligner la grille avec les lignes")

    b.image_rotation(st.session_state["ex_rotation-degree"])
    col1, col2 = st.columns([0.5, 0.5], gap="small")
    with col1:
        st.image(b.plot_scan(b.img))
    with col2:
        st.image(b.plot_scan(b.img_rot))
# Box extraction
    @st.experimental_fragment
    def box_extraction_process():
        b.extract_boxes_fast()
        st.write(f"Boites extraites avec la rotation {st.session_state['ex_rotation-degree']} : dimensions {b.box_coord.shape}")
        with st.expander("Voir/Cacher les boites détectées"):
            st.image(b.plot_boxes(b.box_coord))
        st.session_state['ex_box_coord'] = b.box_coord
    if st.button("Détecter les boites"):
        box_extraction_process()
    start_roi_extraction = 'ex_box_coord' in st.session_state and len(st.session_state.get('ex_box_coord', [])) == 400
# ROI image extraction
    if start_roi_extraction:
        def store_roi_symbols():
            r = extract.ROIExtract(b.img_rot)
            r.extract_roi_symbols(st.session_state['ex_box_coord'])
            st.write(f'Symboles extraits : dimension {r.roi_symbols.shape}')
            st.session_state['ex_roi_symbols'] = r.roi_symbols
            st.session_state['sheet_labels'] = r.sheet_labels
            st.session_state['blank_labels'] = r.blank_labels
        if st.button("Extraire les symboles"):
            store_roi_symbols()

if 'ex_roi_symbols' in st.session_state:

        img_display.roi_display(prefix="ex")
        st.write("Continuer avec la correction ou l'annotation des données via le menu latéral")

st.write(st.session_state)