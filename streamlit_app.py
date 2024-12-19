import os
import streamlit as st

# Set the base directory for audio files
BASE_DIR = "audio_files"

# Title and Instructions
st.title("Dynamic Audio Assignment")
st.write("""
Enter your User ID to get your assigned set of audio samples. 
Listen to the audio and provide transcriptions in the input boxes.
""")

# User Input for ID
user_id = st.text_input("Enter Your User ID:", value="", key="user_id")

if user_id:
    try:
        # Calculate the modulo to determine the directory
        user_id = int(user_id)
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
                    st.success("Your transcriptions have been submitted!")
                    st.write("Here are your responses:")
                    st.json(transcriptions)

    except ValueError:
        st.error("Please enter a valid numerical User ID.")
