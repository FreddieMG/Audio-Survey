import streamlit as st

def main():
    st.title("Audio Perception Experiment")

    # Survey Description
    st.write("""
    ### Welcome to the Audio Perception Experiment

    You are invited to participate in an experiment examining the effect of audio perturbations and transformations on human perception and understanding.

    **Overview of the Study:**
    - In the first part, we will play speech recordings for you. After hearing the audio sample, you will transcribe the audio in the text box. Please listen to the audio once and transcribe to the best of your abilities.
    - In the second part, we will display a larger variety of audio samples, all transformed using several different methods. For each audio sample, you will rate the audio for pleasantness and clarity.
    - After finishing each section, click on the "Submit and Commit" button to save your results.

    **Details:**
    - The experiment will take approximately 40 minutes.
    - As a token of appreciation, you will receive a payment of 50 ₪.

    **Participation Rights:**
    - You may stop participating at any time by closing this window. However, please note that closing the window will prevent your data from being saved, and you will not receive the payment.

    Thank you for your cooperation!
    """)

    # Check if User ID has already been submitted
    if "user_id" in st.session_state:
        st.success("User ID saved successfully! You can now navigate to the sections using the sidebar.")
        return  # Prevent form rendering

    # User ID Form
    with st.form(key="user_id_form"):
        user_id = st.text_input("Please enter your User ID to begin:", key="user_id_input")
        submit_button = st.form_submit_button("Submit User ID")

        if submit_button:
            if user_id.isdigit():
                st.session_state.user_id = user_id
                st.success("User ID saved successfully! You can now navigate to the sections using the sidebar.")
                st.rerun()  # Force rerun to update navigation
            else:
                st.error("User ID must be a numeric value. Please try again.")
# Sidebar Navigation
def navigation():
    st.sidebar.title("Navigation")

    # Display navigation options or a warning based on the presence of User ID
    if "user_id" not in st.session_state:
        st.sidebar.warning("Enter your User ID on the main page to proceed.")
        main()  # Force display of the main page if no User ID
    else:
        page = st.sidebar.radio(
            "Sections",
            ["Main", "Absorption", "Room Shape", "Rotation Speed", "Part 2"]
        )

        # Navigate to the selected page
        if page == "Main":
            main()
        elif page == "Absorption":
            import absorption
            absorption.main()
        elif page == "Room Shape":
            import room_shape
            room_shape.main()
        elif page == "Rotation Speed":
            import rotation_speed
            rotation_speed.main()
        elif page == "Part 2":
            import audio_rating_ver1
            audio_rating_ver1.main()
if __name__ == "__main__":
    navigation()
