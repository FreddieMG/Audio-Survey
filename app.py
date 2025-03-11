import streamlit as st

def introduction_part_1():
    st.markdown(
        """
        <style>
        h1 { font-size: 64px !important; }
        h2 { font-size: 32px !important; }
        p, li { font-size: 20px !important; }
        </style>
        """, unsafe_allow_html=True
    )
    st.title("Welcome to Part 1: Transcription Tasks")
    st.write("""
    In Part 1, you will complete three transcription tasks. 
    - In each task, you will listen to audio samples and transcribe what you hear. 
    - After completing one task, you will proceed to the next.

    Click "Begin Part 1" to begin.
    """)
    if st.button("Begin Part 1"):
        st.session_state.current_page = "Absorption"
        st.rerun()

def introduction_part_2():
    st.markdown(
        """
        <style>
        h1 { font-size: 64px !important; }
        h2 { font-size: 32px !important; }
        p, li { font-size: 20px !important; }
        </style>
        """, unsafe_allow_html=True
    )
    st.title("Welcome to Part 2: Audio Rating Survey")
    st.write("""
    In Part 2, you will rate audio samples on two scales:
    - **Pleasantness**: How pleasant was the audio experience?
    - **Clarity**: How clearly could you understand the spoken content?

    After completing Part 2, your results will be saved, and you will complete the experiment.

    Click "Begin Part 2" to start the Audio Rating survey.
    """)
    if st.button("Begin Part 2"):
        st.session_state.current_page = "Audio Rating"
        st.rerun()

def main():
    st.markdown(
        """
        <style>
        h1 { font-size: 64px !important; }
        h2 { font-size: 32px !important; }
        p, li { font-size: 20px !important; }
        </style>
        """, unsafe_allow_html=True
    )
    st.title("Audio Perception Experiment")

    # Survey Description
    st.write("""
    ### Welcome to the Audio Perception Experiment

    You are invited to participate in an experiment examining the effect of audio perturbations and transformations on human perception and understanding.

    **Overview of the Study:**
    - In the first part, we will play speech recordings for you. After hearing the audio sample, you will transcribe the audio in the text box. Please listen to the audio (no more than three times) and transcribe to the best of your abilities.
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
        user_id = st.text_input("Please enter your ID to begin:", key="user_id_input")
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

    # Check if User ID is set
    if "user_id" not in st.session_state:
        st.sidebar.warning("Enter your User ID on the main page to proceed.")
        main()  # Force display of the main page if no User ID
    else:
        # Initialize part and page tracking
        if "current_part" not in st.session_state:
            st.session_state.current_part = "Part 1"
        if "current_page" not in st.session_state:
            st.session_state.current_page = "Introduction Part 1"

        # Handle transitions
        if st.session_state.current_part == "Part 1":
            if st.session_state.current_page == "Introduction Part 1":
                introduction_part_1()
            elif st.session_state.current_page == "Absorption":
                import absorption
                absorption.main()
            elif st.session_state.current_page == "Room Shape":
                import room_shape
                room_shape.main()
            elif st.session_state.current_page == "Rotation Speed":
                import rotation_speed
                rotation_speed.main()
                
        elif st.session_state.current_part == "Part 2":
            if st.session_state.current_page == "Introduction Part 2":
                introduction_part_2()
            else:  # Default to Audio Rating
                import audio_rating_ver1
                audio_rating_ver1.main()

if __name__ == "__main__":
    navigation()