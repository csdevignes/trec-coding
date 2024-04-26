'''

'''

import extract
import streamlit as st

def store_value(key):
    st.session_state[key] = st.session_state["_"+key]
def load_value(key):
    st.session_state["_"+key] = st.session_state[key]

image_file = "Test.png"
image_path = f"scan_resultsheets/{image_file}"
st.write(image_path)
b = extract.Boxdetection(image_path)

if "rotation-degree" not in st.session_state:
    st.session_state["rotation-degree"] = 0
load_value("rotation-degree")
st.number_input('Rotation degree', min_value=-360., max_value=360.,
                         step=0.01, key="_rotation-degree", on_change=store_value,
                         args=["rotation-degree"],
                         help="Adjust rotation so the grid is aligned on the lines")

b.image_rotation(st.session_state["rotation-degree"])
col1, col2 = st.columns([0.5, 0.5], gap="small")
with col1:
    st.image(b.plot_scan(b.img))
with col2:
    st.image(b.plot_scan(b.img_rot))

st.button("Click me")

st.write(st.session_state)