import os
import random
import re
import streamlit as st
import pandas as pd
from jiwer import wer
from supabase import create_client, Client

# Set the base directory for audio files
BASE_DIR = "audio_samples/absorption_Exp"

# Absorption levels
absorptions = [0.1, 0.2, 0.3, 0.4, 0.5]

# Load reference transcriptions
def load_reference_transcriptions():
    abs_transcriptions = {}
    df = pd.read_csv("abs_exp_transcription.csv")
    for indx, row in df.iterrows():
        abs_transcriptions[f'{indx}.wav'] = row['transcription']
    return abs_transcriptions

reference_transcriptions = load_reference_transcriptions()

# Initialize session state variables
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

if 'audio_assignments' not in st.session_state:
    st.session_state.audio_assignments = {}

if 'current_audio_index' not in st.session_state:
    st.session_state.current_audio_index = 0

if 'transcriptions' not in st.session_state:
    st.session_state.transcriptions = {}

if 'show_indicator' not in st.session_state:
    st.session_state.show_indicator = False

if 'completed' not in st.session_state:
    st.session_state.completed = False

# Supabase client setup
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Assign audio files to user without duplicates within the same user
def assign_audio_files():
    audio_assignments = {}
    first_absorption_dir = os.path.join(BASE_DIR, str(absorptions[0]))
    if not os.path.exists(first_absorption_dir):
        st.error(f"Directory for absorption {absorptions[0]} does not exist.")
        return audio_assignments  # Empty assignments

    audio_files = [f for f in os.listdir(first_absorption_dir) if f.endswith(".wav")]
    random.shuffle(audio_files)

    for absorption in absorptions:
        if not audio_files:
            break
        audio_assignments[absorption] = audio_files.pop(0)

    return audio_assignments

# Clean text for WER calculation
def clean_text(text):
    return re.sub(r'[^a-zA-Z\s]', '', text).lower()

def save_results_to_supabase(user_id):
    # Prepare the data for insertion
    values = [None] * len(absorptions)

    for absorption, audio_file in st.session_state.audio_assignments.items():
        user_transcription = st.session_state.transcriptions.get(absorptions.index(absorption) + 1, "")
        reference_transcription = reference_transcriptions.get(audio_file, "")

        if reference_transcription:
            error_rate = wer(clean_text(reference_transcription), clean_text(user_transcription))
            values[absorptions.index(absorption)] = error_rate

    # Data payload
    data = {
        "uid": user_id,  # Ensure to use "uid" as in the schema
        "0.1": values[0],
        "0.2": values[1],
        "0.3": values[2],
        "0.4": values[3],
        "0.5": values[4],
    }

    # Insert or update data in Supabase
    response = supabase.table("absorption").upsert(data).execute()
    print(response)
    

# Main Application
def main():
    st.title("Dynamic Audio Assignment")
    st.write("""
    Enter your User ID to receive your set of audio samples for transcription. Your User ID will be logged for tracking purposes.
    """)

    user_input = st.text_input("Enter Your User ID:", value="", key="user_input")

    if user_input:
        try:
            # Convert User ID to integer
            user_id = int(user_input)

            if st.session_state.user_id != user_id:
                st.session_state.user_id = user_id
                st.session_state.audio_assignments = assign_audio_files()
                st.session_state.current_audio_index = 0
                st.session_state.transcriptions = {}
                st.session_state.completed = False
                st.success(f"User ID {user_id} has been recognized and audio assignments have been made.")

            # Prepare a list of assignments excluding None values
            valid_assignments = [
                (absorption, audio_file)
                for absorption, audio_file in st.session_state.audio_assignments.items()
                if audio_file is not None
            ]

            total_audios = len(valid_assignments)

            if not st.session_state.completed and st.session_state.current_audio_index < total_audios:
                # Display submission indicator if flag is set
                if st.session_state.show_indicator:
                    st.success("Transcription submitted successfully and a new audio sample has been allocated.")
                    st.session_state.show_indicator = False

                audio_number = st.session_state.current_audio_index + 1
                absorption, audio_file = valid_assignments[st.session_state.current_audio_index]

                audio_path = os.path.join(BASE_DIR, str(absorption), audio_file)

                if not os.path.exists(audio_path):
                    st.error(f"Audio file {audio_file} does not exist in {str(absorption)}.")
                    return

                # Retrieve existing transcription if available
                existing_transcription = st.session_state.transcriptions.get(audio_number, "")

                # Display audio and transcription input within a form
                with st.form(key="transcription_form"):
                    st.subheader(f"Audio Sample {audio_number} of {total_audios}")
                    st.write(
                        "Please transcribe this audio to the best of your abilities. If you only understood part of it, write down all the words you did understand.")
                    st.audio(audio_path, format="audio/wav")
                    transcription = st.text_area("Enter transcription for the above audio:",
                                                 value=existing_transcription,
                                                 key=f"transcription_{user_id}_{audio_number}")

                    # Submit Button
                    submit_button = st.form_submit_button(label=f"Submit Audio {audio_number}")

                # 'Go Back' Button
                if st.button("Go Back"):
                    if st.session_state.current_audio_index > 0:
                        st.session_state.current_audio_index -= 1
                        st.rerun()
                    else:
                        st.warning("You are at the first audio sample.")

                if submit_button:
                    if not transcription.strip():
                        st.warning("Please enter a transcription before submitting.")
                    else:
                        # Save transcription to session state
                        st.session_state.transcriptions[audio_number] = transcription

                        # Set the submission indicator flag
                        st.session_state.show_indicator = True

                        # Update progress
                        st.session_state.current_audio_index += 1

                        # Rerun the app to load the next audio
                        st.rerun()

            elif not st.session_state.completed:
                st.success("You have completed all audio samples for this session. Thank you!")
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Commit and Save"):
                        save_results_to_supabase(st.session_state.user_id)
                        st.session_state.completed = True
                        st.success("All transcriptions have been saved. You may close the session.")

                with col2:
                    if st.button("Go Back"):
                        st.session_state.current_audio_index -= 1
                        st.rerun()

        except ValueError:
            st.error("Please enter a valid numerical User ID.")

if __name__ == "__main__":
    main()
