import streamlit as st

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select Experiment", ["Absorption", "Room Shape", "Rotation Speed"])

if page == "Absorption":
    import absorption
    absorption.main()
elif page == "Room Shape":
    import room_shape
    room_shape.main()
elif page == "Rotation Speed":
    import rotation_speed
    rotation_speed.main()
