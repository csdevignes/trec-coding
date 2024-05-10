'''
TREC correction app - page 1
This page aims to upload file, and extract images
'''


import numpy as np
import streamlit as st
import extract
import sidebar

sidebar.sidebar_progress()

# Loading and rotating scan
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
    if 'res' not in st.session_state:
        st.session_state.res = {}
# Box extraction
    @st.experimental_fragment
    def box_extraction_test():
        for threshold in range(256):
            b.find_boxes(threshold)
            st.session_state.res[threshold] = b.box_coord.shape
    if st.button("Détecter les boites"):
        box_extraction_test()

    detecting_TS = [i if st.session_state.res[i][0] == 400 else 'False' for i in st.session_state.res.keys()]
    st.write(f'400 boxes detected for thresholds: ')
    st.write(*detecting_TS)