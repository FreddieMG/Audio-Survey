import os
import random
import streamlit as st
import csv

# Set the base directory for audio files
BASE_DIR = "audio_samples/absorption_Exp"

# Directory to store user results
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)  # Ensure the results directory exists

# File paths
CSV_FILE = os.path.join(RESULTS_DIR, "results.csv")

# Absorption levels
absorptions = [0.1, 0.2, 0.3, 0.4, 0.5]

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

# Initialize CSV file
def initialize_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["User ID", "Audio Number", "Audio File", "Transcription"])

# Save transcription to CSV
def save_transcription(user_id, audio_number, audio_file, transcription):
    with open(CSV_FILE, "a", newline="", encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([user_id, audio_number, audio_file, transcription])

# Assign audio files to user without duplicates within the same user
def assign_audio_files():
    audio_assignments = {}
    
    # Assume all absorption directories have the same audio file names
    first_absorption_dir = os.path.join(BASE_DIR, str(absorptions[0]))
    if not os.path.exists(first_absorption_dir):
        st.error(f"Directory for absorption {absorptions[0]} does not exist.")
        return audio_assignments  # Empty assignments

    # List of audio files from the first absorption directory
    audio_files = [f for f in os.listdir(first_absorption_dir) if f.endswith(".wav")]

    if not audio_files:
        st.error("No audio files found in the first absorption directory.")
        return audio_assignments  # Empty assignments

    # Shuffle the audio files to ensure randomness
    random.shuffle(audio_files)

    for absorption in absorptions:
        absorption_str = str(absorption)
        cur_dir = os.path.join(BASE_DIR, absorption_str)

        if not os.path.exists(cur_dir):
            st.error(f"Directory for absorption {absorption} does not exist.")
            audio_assignments[absorption] = None
            continue

        if not audio_files:
            st.warning(f"No remaining audio files to assign for absorption {absorption}.")
            audio_assignments[absorption] = None
            continue

        # Select the first available audio file and remove it to prevent duplicates
        selected_audio = audio_files.pop(0)
        audio_assignments[absorption] = selected_audio

    return audio_assignments

# Main Application
def main():
    st.title("Dynamic Audio Assignment")
    st.write("""
    Enter your User ID to receive your set of audio samples for transcription. 
    Your User ID will be logged for tracking purposes.
    """)

    user_input = st.text_input("Enter Your User ID:", value="", key="user_input")

    if user_input:
        try:
            # Convert User ID to integer
            user_id = int(user_input)

            # Assign audio files if not already assigned
            if st.session_state.user_id != user_id:
                st.session_state.user_id = user_id
                st.session_state.audio_assignments = assign_audio_files()
                st.session_state.current_audio_index = 0
                st.session_state.transcriptions = {}  # Reset transcriptions

                if st.session_state.audio_assignments:
                    st.success(f"User ID {user_id} has been recognized and audio assignments have been made.")
                else:
                    st.error("Audio assignments could not be completed due to missing directories or audio files.")
                    return

            # Initialize CSV
            initialize_csv()

            # Prepare a list of assignments excluding None values
            valid_assignments = [
                (absorption, audio_file)
                for absorption, audio_file in st.session_state.audio_assignments.items()
                if audio_file is not None
            ]

            total_audios = len(valid_assignments)

            if st.session_state.current_audio_index < total_audios:
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
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button("Go Back"):
                        if st.session_state.current_audio_index > 0:
                            st.session_state.current_audio_index -= 1
                            st.rerun()
                        else:
                            st.warning("You are at the first audio sample.")
                with col2:
                    pass  # Placeholder for layout purposes

                if submit_button:
                    if not transcription.strip():
                        st.warning("Please enter a transcription before submitting.")
                    else:
                        # Save transcription to session state
                        st.session_state.transcriptions[audio_number] = transcription

                        # Save transcription to CSV
                        save_transcription(user_id, audio_number, audio_file, transcription)

                        # Set the submission indicator flag
                        st.session_state.show_indicator = True

                        # Update progress
                        st.session_state.current_audio_index += 1

                        # Rerun the app to load the next audio
                        st.rerun()

            else:
                st.success("You have completed all audio samples for this session. Thank you!")

        except ValueError:
            st.error("Please enter a valid numerical User ID.")

if __name__ == "__main__":
    main()
