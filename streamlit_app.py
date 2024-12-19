import os
import random
import streamlit as st
import json
import csv

# Set the base directory for audio files
BASE_DIR = "audio_samples/absorption_Exp/absorption"

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

# User Input for ID
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

        # Track the current absorption level for the user
        user_results_dir = os.path.join(RESULTS_DIR, str(user_id))
        os.makedirs(user_results_dir, exist_ok=True)

        progress_file = os.path.join(user_results_dir, "progress.json")
        csv_file = os.path.join(RESULTS_DIR, "results.csv")

        # Initialize CSV if it doesn't exist
        if not os.path.exists(csv_file):
            with open(csv_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["User ID", "Absorption", "Audio File", "Transcription"])

        # Load progress if it exists, otherwise start from the first absorption
        if os.path.exists(progress_file):
            with open(progress_file, "r") as f:
                progress = json.load(f)
        else:
            progress = {"current_absorption_index": 0, "completed": []}

        current_absorption_index = progress["current_absorption_index"]

        if current_absorption_index < len(absorptions):
            current_absorption = absorptions[current_absorption_index]

            # List all audio files for the current absorption level
            audio_files = [f for f in os.listdir(BASE_DIR) if f.endswith(".wav") and f"_{current_absorption_index}" in f]

            if not audio_files:
                st.warning(f"No audio files found for absorption {current_absorption}.")
            else:
                # Select a random audio file
                audio_file = random.choice(audio_files)
                audio_path = os.path.join(BASE_DIR, audio_file)

                # Display audio and transcription input
                st.subheader(f"Absorption Level: {current_absorption}")
                st.audio(audio_path, format="audio/wav")

                transcription = st.text_area("Enter transcription for the above audio:")

                # Submit Button
                if st.button("Submit Transcription"):
                    # Save transcription to CSV
                    with open(csv_file, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([user_id, current_absorption, audio_file, transcription])

                    # Update progress
                    progress["completed"].append(current_absorption_index)
                    progress["current_absorption_index"] += 1
                    with open(progress_file, "w") as f:
                        json.dump(progress, f, indent=4)

                    st.success("Transcription submitted. Loading next audio sample...")
                    st.experimental_rerun()

        else:
            st.success("You have completed all audio samples for this session. Thank you!")

    except ValueError:
        st.error("Please enter a valid numerical User ID.")
