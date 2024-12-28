import os
import streamlit as st
from utils.common import assign_audio_files 
from utils.transcription_utils import load_reference_transcriptions, clean_text
from utils.db_utils import get_supabase_client, save_results_to_supabase


BASE_DIR = "audio_samples/room_shape_Exp"
CSV_FILE = "room_exp_transcription.csv"
TABLE_NAME = "room_shape"
PARAMETERS = ["(40, 3)", "(30, 10)", "(20, 20)", "(10, 30)", "(3, 40)"]

reference_transcriptions = load_reference_transcriptions(CSV_FILE)


def main():
    st.title("Room Shape Experiment")
    user_id = st.text_input("Enter Your User ID", key="room_shape_user_input")

    # Initialize session state variables
    if "room_shape_user_id" not in st.session_state:
        st.session_state.room_shape_user_id = None
    if "room_shape_audio_assignments" not in st.session_state:
        st.session_state.room_shape_audio_assignments = {}
    if "room_shape_current_audio_index" not in st.session_state:
        st.session_state.room_shape_current_audio_index = 0
    if "room_shape_transcriptions" not in st.session_state:
        st.session_state.room_shape_transcriptions = {}
    if "room_shape_completed" not in st.session_state:
        st.session_state.room_shape_completed = False
    if "room_shape_show_indicator" not in st.session_state:
        st.session_state.room_shape_show_indicator = False

    # Process user input
    if user_id:
        st.session_state.room_shape_user_id = user_id

        # Assign audio files if not already assigned
        if not st.session_state.room_shape_audio_assignments:
            st.session_state.room_shape_audio_assignments = assign_audio_files(BASE_DIR, PARAMETERS)

        valid_assignments = st.session_state.room_shape_audio_assignments
        total_audios = len(valid_assignments)

        if not st.session_state.room_shape_completed and st.session_state.room_shape_current_audio_index < total_audios:
            # Display submission indicator if flag is set
            if st.session_state.room_shape_show_indicator:
                st.success("Transcription submitted successfully and a new audio sample has been allocated.")
                st.session_state.room_shape_show_indicator = False

            audio_number = st.session_state.room_shape_current_audio_index + 1
            parameter, audio_path = list(valid_assignments.items())[st.session_state.room_shape_current_audio_index]

            # Display audio and transcription input within a form
            with st.form(key="transcription_form"):
                st.subheader(f"Audio Sample {audio_number} of {total_audios}")
                st.write(
                    "Please transcribe this audio to the best of your abilities. If you only understood part of it, write down all the words you did understand."
                )
                st.audio(audio_path, format="audio/wav")
                existing_transcription = st.session_state.room_shape_transcriptions.get(audio_number, "")
                transcription = st.text_area(
                    "Enter transcription for the above audio:",
                    value=existing_transcription,
                    key=f"room_shape_transcription_{user_id}_{audio_number}",
                )

                # Submit Button
                submit_button = st.form_submit_button(label=f"Submit Audio {audio_number}")

            # 'Go Back' Button
            if st.button("Go Back"):
                if st.session_state.room_shape_current_audio_index > 0:
                    st.session_state.room_shape_current_audio_index -= 1
                    st.rerun()
                else:
                    st.warning("You are at the first audio sample.")

            if submit_button:
                if not transcription.strip():
                    st.warning("Please enter a transcription before submitting.")
                else:
                    # Save transcription to session state
                    st.session_state.room_shape_transcriptions[audio_number] = transcription

                    # Set the submission indicator flag
                    st.session_state.room_shape_show_indicator = True

                    # Update progress
                    st.session_state.room_shape_current_audio_index += 1

                    # Rerun the app to load the next audio
                    st.rerun()

        elif not st.session_state.room_shape_completed:
            st.success("You have completed all audio samples for this section of the experiment.")
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("Commit and Save"):
                    save_results_to_supabase(
                        st.session_state.room_shape_user_id,
                        TABLE_NAME,
                        st.session_state.room_shape_transcriptions,
                        PARAMETERS,
                        "abs_exp_transcription.csv",
                    )
                    st.session_state.room_shape_completed = True
                    st.success(
                        "All transcriptions have been saved. You have finished this section of the experiment. "
                        "Please proceed to the other sections."
                    )

            with col2:
                if st.button("Go Back"):
                    st.session_state.room_shape_current_audio_index -= 1
                    st.rerun()
