import streamlit as st

# --- Global typography ---
st.markdown(
    """
    <style>
    h1 { font-size: 64px !important; }
    h2 { font-size: 32px !important; }
    p, li { font-size: 20px !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

def introduction():
    st.title("Welcome to the Audio Rating Survey")
    st.write("""
    In this survey, you will rate audio samples on two scales:
    - **Pleasantness**: How pleasant was the audio experience?
    - **Clarity**: How clearly could you understand the spoken content?

    After completing the survey, your results will be saved and the experiment will end.

    Click **Begin** to start the Audio Rating survey.
    """)
    if st.button("Begin"):
        st.session_state.current_page = "Audio Rating"
        st.rerun()

def main():
    st.title("Audio Perception Experiment")

    st.write("""
    ### Welcome to the Audio Perception Experiment

    You are invited to participate in an experiment examining the effect of audio
    perturbations and transformations on human perception.

    **Overview:**
    - You will listen to audio recordings that have been transformed using several different methods.
    - For each audio sample, you will rate the audio for **pleasantness** and **clarity**.
    - After finishing, your results will be saved.

    **Details:**
    - The experiment will take approximately 10 minutes.
    - As a token of appreciation, you will receive a payment of 25 ₪.

    **Participation Rights:**
    - You may stop participating at any time by closing this window. However, closing the window prevents your data from being saved, and you will not receive the payment.
    """)

    # If we already have a user_id, jump straight to the intro screen
    if "user_id" in st.session_state:
        st.info("Your ID is saved. Click **Begin** to start the survey.")
        st.session_state.current_page = "Introduction"
        return

    # Ask for ID once
    with st.form(key="user_id_form"):
        user_id = st.text_input("Please enter your ID to begin:", key="user_id_input")
        submit_button = st.form_submit_button("Submit ID")
        if submit_button:
            if user_id.isdigit():
                st.session_state.user_id = user_id
                st.session_state.current_page = "Introduction"
                st.success("ID saved. Loading the survey...")
                st.rerun()
            else:
                st.error("User ID must be a numeric value. Please try again.")

def navigation():
    # Optional: minimal sidebar just to show status
    st.sidebar.title("Status")
    if "user_id" not in st.session_state:
        st.sidebar.warning("Enter your User ID on the main page to proceed.")
        main()
        return

    st.sidebar.success(f"ID: {st.session_state.user_id}")

    # Page state machine
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Introduction"

    if st.session_state.current_page == "Introduction":
        introduction()
    elif st.session_state.current_page == "Audio Rating":
        import audio_rating_audioshield
        audio_rating_audioshield.main()
    else:
        # Fallback to intro if state is unexpected
        st.session_state.current_page = "Introduction"
        st.rerun()

if __name__ == "__main__":
    navigation()
