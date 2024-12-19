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

# Directory to store user IDs
USER_IDS_FILE = os.path.join(RESULTS_DIR, "user_ids.json")

# Load existing user IDs
if os.path.exists(USER_IDS_FILE):
    with open(USER_IDS_FILE, "r") as f:
        saved_user_ids = json.load(f)
else:
    saved_user_ids = []

# Absorption levels
absorptions = [0.1, 0.2, 0.3, 0.4, 0.5]

# Title and Instructions
st.title("Dynamic Audio Assignment")
st.write("""
Enter your User ID to get your assigned set of audio samples. 
Your User ID will be logged for tracking purposes.
""")

user_id = st.text_input("Enter Your User ID:", value="", key="user_id")

if user_id:
    try:
        # Convert User ID to integer
        user_id = int(user_id)

        # Save the User ID if not already saved
        if user_id not in saved_user_ids:
            saved_user_ids.append(user_id)
            with open(USER_IDS_FILE, "w") as f:
                json.dump(saved_user_ids, f, indent=4)

        st.success(f"User ID {user_id} has been saved.")

        # Directory to store CSV results
        csv_file = os.path.join(RESULTS_DIR, "results.csv")

        # Initialize CSV if it doesn't exist
        if not os.path.exists(csv_file):
            with open(csv_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["User ID", "Audio Number", "Audio File", "Transcription"])

        # Load current progress for the user
        progress_file = os.path.join(RESULTS_DIR, f"progress_{user_id}.json")
        if os.path.exists(progress_file):
            with open(progress_file, "r") as f:
                progress = json.load(f)
        else:
            progress = {"current_audio_index": 0}

        current_audio_index = progress["current_audio_index"]

        if current_audio_index < len(absorptions):
            absorption = absorptions[current_audio_index]
            cur_dir = os.path.join(BASE_DIR, str(absorption))
            audio_files = [f for f in os.listdir(cur_dir) if f.endswith(".wav")]

            if not audio_files:
                st.warning(f"No audio files found for the current level.")
            else:
                # Select a random audio file
                audio_file = random.choice(audio_files)
                audio_path = os.path.join(cur_dir, audio_file)

                # Display audio and transcription input
                st.subheader(f"Audio Sample {current_audio_index + 1}")
                st.write("Please transcribe this audio to the best of your abilities. If you only understood part of it, write down all the words you did understand.")
                st.audio(audio_path, format="audio/wav")

                transcription_key = f"transcription_{user_id}_{current_audio_index}"
                transcription = st.text_area("Enter transcription for the above audio:", key=transcription_key)

                # Submit Button
                if st.button(f"Submit Audio {current_audio_index + 1}"):
                    if not transcription.strip():
                        st.warning("Please enter a transcription before submitting.")
                    else:
                        # Save transcription to CSV
                        with open(csv_file, "a", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerow([user_id, current_audio_index + 1, audio_file, transcription])

                        # Update progress
                        progress["current_audio_index"] += 1
                        with open(progress_file, "w") as f:
                            json.dump(progress, f, indent=4)

                        # Clear session state and reload
                        st.session_state.clear()
                        st.session_state["user_id"] = str(user_id)
                        st.experimental_set_query_params(dummy=str(random.random()))
        else:
            st.success("You have completed all audio samples for this session. Thank you!")

    except ValueError:
        st.error("Please enter a valid numerical User ID.")
