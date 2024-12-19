import os
import random
import streamlit as st
import json
import csv

# Set the base directory for audio files
BASE_DIR = "audio_samples/absorption_Exp"

# Directory to store user results
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)  # Ensure the results directory exists

# File paths
USER_IDS_FILE = os.path.join(RESULTS_DIR, "user_ids.json")
CSV_FILE = os.path.join(RESULTS_DIR, "results.csv")

# Absorption levels
absorptions = [0.1, 0.2, 0.3, 0.4, 0.5]

# Initialize session state for user_id, audio_assignments, and current_audio_index
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

if 'audio_assignments' not in st.session_state:
    st.session_state.audio_assignments = {}

if 'current_audio_index' not in st.session_state:
    st.session_state.current_audio_index = 0

# Load existing user IDs
def load_user_ids():
    if os.path.exists(USER_IDS_FILE):
        with open(USER_IDS_FILE, "r") as f:
            return json.load(f)
    return []

# Save user IDs
def save_user_ids(user_ids):
    with open(USER_IDS_FILE, "w") as f:
        json.dump(user_ids, f, indent=4)

# Initialize CSV file
def initialize_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["User ID", "Audio Number", "Audio File", "Transcription"])

# Save transcription to CSV
def save_transcription(user_id, audio_number, audio_file, transcription):
    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([user_id, audio_number, audio_file, transcription])

# Assign audio files to user based on user_id
def assign_audio_files(user_id):
    assignments = {}
    for idx, absorption in enumerate(absorptions):
        cur_dir = os.path.join(BASE_DIR, str(absorption))
        if not os.path.exists(cur_dir):
            st.error(f"Directory for absorption {absorption} does not exist.")
            continue

        audio_files = [f for f in os.listdir(cur_dir) if f.endswith(".wav")]
        if not audio_files:
            st.warning(f"No audio files found for absorption level {absorption}.")
            continue

        # Deterministic assignment using modulo to ensure even distribution
        audio_file = audio_files[user_id % len(audio_files)]
        assignments[idx] = audio_file
    return assignments

# Main Application
def main():
    st.title("Dynamic Audio Assignment")
    st.write("""
    Enter your User ID to get your assigned set of audio samples. 
    Your User ID will be logged for tracking purposes.
    """)

    user_input = st.text_input("Enter Your User ID:", value="", key="user_input")

    if user_input:
        try:
            # Convert User ID to integer
            user_id = int(user_input)

            # Load and update user IDs
            user_ids = load_user_ids()
            if user_id not in user_ids:
                user_ids.append(user_id)
                save_user_ids(user_ids)
                st.success(f"User ID {user_id} has been saved.")
            else:
                st.info(f"User ID {user_id} recognized.")

            # Assign audio files if not already assigned
            if st.session_state.user_id != user_id:
                st.session_state.user_id = user_id
                st.session_state.audio_assignments = assign_audio_files(user_id)
                st.session_state.current_audio_index = 0

            # Initialize CSV
            initialize_csv()

            if st.session_state.current_audio_index < len(absorptions):
                audio_number = st.session_state.current_audio_index + 1
                audio_file = st.session_state.audio_assignments.get(st.session_state.current_audio_index, None)

                if audio_file:
                    # Construct the audio path
                    # Find which absorption this audio file belongs to
                    assigned_absorption = absorptions[st.session_state.current_audio_index]
                    audio_path = os.path.join(BASE_DIR, str(assigned_absorption), audio_file)

                    # Display audio and transcription input within a form
                    with st.form(key="transcription_form"):
                        st.subheader(f"Audio Sample {audio_number}")
                        st.write("Please transcribe this audio to the best of your abilities. If you only understood part of it, write down all the words you did understand.")
                        st.audio(audio_path, format="audio/wav")
                        transcription = st.text_area("Enter transcription for the above audio:", key=f"transcription_{user_id}_{audio_number}")

                        # Submit Button
                        submit_button = st.form_submit_button(label=f"Submit Audio {audio_number}")

                        if submit_button:
                            if not transcription.strip():
                                st.warning("Please enter a transcription before submitting.")
                            else:
                                # Save transcription to CSV
                                save_transcription(user_id, audio_number, audio_file, transcription)

                                st.success("Transcription submitted successfully!")

                                # Update progress
                                st.session_state.current_audio_index += 1

                                # Rerun the app to load the next audio
                                st.rerun()
                else:
                    st.warning("No audio file assigned for this sample.")
            else:
                st.success("You have completed all audio samples for this session. Thank you!")

        except ValueError:
            st.error("Please enter a valid numerical User ID.")

if __name__ == "__main__":
    main()
