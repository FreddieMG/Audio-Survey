import os
import streamlit as st
import json

# Set the base directory for audio files
BASE_DIR = "audio_files"

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

        # If the User ID is 209258912, show a download button for the user_ids.json file
        if user_id == 209258912:
            st.info("You have special access to download the user IDs log file.")
            if os.path.exists(USER_IDS_FILE):
                with open(USER_IDS_FILE, "r") as f:
                    user_ids_data = f.read()
                st.download_button(
                    label="Download User IDs Log",
                    data=user_ids_data,
                    file_name="user_ids.json",
                    mime="application/json"
                )

        # Calculate the modulo to determine the directory
        folder_index = user_id % 7
        folder_path = os.path.join(BASE_DIR, str(folder_index))

        # Check if the folder exists
        if not os.path.exists(folder_path):
            st.error(f"Audio folder for ID modulo {folder_index} does not exist.")
        else:
            st.success(f"You have been assigned to folder {folder_index}.")

            # List all audio files in the assigned folder
            audio_files = [f for f in os.listdir(folder_path) if f.endswith(".mp3")]

            if not audio_files:
                st.warning("No audio files found in this folder.")
            else:
                # Display audio players and transcription input fields
                transcriptions = {}
                for idx, audio_file in enumerate(audio_files, start=1):
                    audio_path = os.path.join(folder_path, audio_file)

                    st.subheader(f"Audio Sample {idx}")
                    st.audio(audio_path, format="audio/mp3")

                    # Text input for transcription
                    transcriptions[audio_file] = st.text_area(
                        f"Transcription for Sample {idx}:", key=f"transcription_{idx}"
                    )

                # Submit Button
                if st.button("Submit Transcriptions"):
                    # Create a user-specific directory
                    user_results_dir = os.path.join(RESULTS_DIR, str(user_id))
                    os.makedirs(user_results_dir, exist_ok=True)

                    # Save the transcriptions to a JSON file in the user's directory
                    result_file = os.path.join(user_results_dir, "transcriptions.json")
                    with open(result_file, "w") as f:
                        json.dump(transcriptions, f, indent=4)

                    st.success(f"Your transcriptions have been saved to {user_results_dir}!")
                    st.write("Here are your responses:")
                    st.json(transcriptions)

    except ValueError:
        st.error("Please enter a valid numerical User ID.")
