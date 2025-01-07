import os
import streamlit as st
from utils.common import assign_audio_files
from utils.transcription_utils import load_reference_transcriptions, clean_text
from utils.db_utils import save_results_to_supabase

BASE_DIR = "audio_samples/absorption_Exp"
CSV_FILE = "abs_exp_transcription.csv"
TABLE_NAME = "absorption"
PARAMETERS = [0.1, 0.2, 0.3, 0.4, 0.5]

reference_transcriptions = load_reference_transcriptions(CSV_FILE)
def main():
    st.title("Absorption Experiment")



    user_id = st.session_state.user_id

    # Initialize session state variables
    if "absorption_audio_assignments" not in st.session_state:
        st.session_state.absorption_audio_assignments = {}
    if "absorption_current_audio_index" not in st.session_state:
        st.session_state.absorption_current_audio_index = 0
    if "absorption_transcriptions" not in st.session_state:
        st.session_state.absorption_transcriptions = {}
    if "absorption_completed" not in st.session_state:
        st.session_state.absorption_completed = False
    if "absorption_show_indicator" not in st.session_state:
        st.session_state.absorption_show_indicator = False

    # Assign audio files if not already assigned
    if not st.session_state.absorption_audio_assignments:
        st.session_state.absorption_audio_assignments = assign_audio_files(BASE_DIR, PARAMETERS)

    valid_assignments = st.session_state.absorption_audio_assignments
    total_audios = len(valid_assignments)

    if not st.session_state.absorption_completed and st.session_state.absorption_current_audio_index < total_audios:
        # Display submission indicator if flag is set
        if st.session_state.absorption_show_indicator:
            st.success("Transcription submitted successfully and a new audio sample has been allocated.")
            st.session_state.absorption_show_indicator = False

        audio_number = st.session_state.absorption_current_audio_index + 1
        parameter, audio_path = list(valid_assignments.items())[st.session_state.absorption_current_audio_index]

        # Display audio and transcription input within a form
        with st.form(key="transcription_form"):
            st.subheader(f"Audio Sample {audio_number} of {total_audios}")
            st.write(
                "Please transcribe this audio to the best of your abilities. If you only understood some of it, write down the parts you did understand."
            )
            st.audio(audio_path, format="audio/wav")
            existing_transcription = st.session_state.absorption_transcriptions.get(parameter, "")
            transcription = st.text_area(
                "Enter transcription for the above audio:",
                value=existing_transcription,
                key=f"absorption_transcription_{user_id}_{audio_number}",
            )

            # Submit Button
            submit_button = st.form_submit_button(label=f"Submit Audio {audio_number}")

        # 'Go Back' Button
        if st.button("Go Back"):
            if st.session_state.absorption_current_audio_index > 0:
                st.session_state.absorption_current_audio_index -= 1
                st.rerun()
            else:
                st.warning("You are at the first audio sample.")

        if submit_button:
            if not transcription.strip():
                st.warning("Please enter a transcription before submitting.")
            else:
                # Save transcription to session state
                st.session_state.absorption_transcriptions[parameter] = transcription

                # Set the submission indicator flag
                st.session_state.absorption_show_indicator = True

                # Update progress
                st.session_state.absorption_current_audio_index += 1

                # Rerun the app to load the next audio
                st.rerun()

    elif not st.session_state.absorption_completed:
        st.success("You have completed all audio samples for this section of the experiment.")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Commit and Save"):
                save_results_to_supabase(
                    user_id,
                    TABLE_NAME,
                    st.session_state.absorption_transcriptions,
                    st.session_state.absorption_audio_assignments,
                    "abs_exp_transcription.csv",
                )
                st.session_state.absorption_completed = True
                st.success(
                    "All transcriptions have been saved. You have finished this section of the experiment. "
                    "Please proceed to the next section."
                )
                                # Redirect to next page
                st.session_state.current_page = "Room Shape"
                st.rerun()

        with col2:
            if not st.session_state.absorption_completed:
                if st.button("Go Back"):
                    st.session_state.absorption_current_audio_index -= 1
                    st.rerun()
