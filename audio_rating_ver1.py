import os
import pandas as pd
import time
import streamlit as st
from utils.db_utils import get_supabase_client

# Load the CSV
CSV_FILE = "part_2_version1.csv"
audio_data = pd.read_csv(CSV_FILE)
audio_data = audio_data.sort_values(["poll_index"])
BASE_DIR = "audio_samples/part2/ver1"

def main():
    st.title("Audio Rating Survey")

    if "current_part" not in st.session_state or st.session_state.current_part != "Part 2":
        st.warning("Please complete Part 1 before starting Part 2.")
        st.stop()
    # Check if User ID is set
    if "user_id" not in st.session_state:
        st.warning("Please return to the main page to enter your User ID.")
        return

    # Initialize session state variables
    if "audio_ratings" not in st.session_state:
        st.session_state.audio_ratings = {}
    if "current_audio_index" not in st.session_state:
        st.session_state.current_audio_index = 0
    if "completed" not in st.session_state:
        st.session_state.completed = False
    if "show_indicator" not in st.session_state:
        st.session_state.show_indicator = False

    total_audios = len(audio_data)

    # Display current audio sample
    if not st.session_state.completed:
        index = st.session_state.current_audio_index
        row = audio_data.iloc[index]

        st.subheader(f"Audio Sample {index + 1} of {total_audios}")
        st.audio(os.path.normpath(os.path.join(BASE_DIR, str(row['poll_index']) + ".wav")), format="audio/wav")

        # Apply custom CSS to improve layout
        st.markdown(
            """
            <style>
                .stRadio > div { flex-direction: column; }
                .stRadio label { font-size: 16px; padding: 8px; }
                .stRadio div[role="radiogroup"] input { width: 20px; height: 20px; margin: 5px; }
                h1, h2, h3 { font-size: 24px; margin-bottom: 12px; }
                .block-container { padding: 20px; max-width: 700px; }
            </style>
            """,
            unsafe_allow_html=True,
        )

        # Retrieve existing ratings if they exist
        existing_ratings = st.session_state.audio_ratings.get(row['poll_index'], {})

        # Rating form with vertical radio buttons
        with st.form(key="rating_form"):
            st.markdown("### How pleasant did you find the audio experience?")
            pleasantness = st.radio(
                label="",
                options=[None, 5, 4, 3, 2, 1],
                index=[None, 5, 4, 3, 2, 1].index(existing_ratings.get("pleasantness", None)),
                format_func=lambda x: f"{x} {'Very Pleasant' if x == 5 else 'Very Unpleasant' if x == 1 else ''}" if x else "No Selection",
                key=f"pleasantness_{index}",
            )

            st.markdown("### How clearly can you understand the spoken content in this audio?")
            clarity = st.radio(
                label="",
                options=[None, 5, 4, 3, 2, 1],
                index=[None, 5, 4, 3, 2, 1].index(existing_ratings.get("clarity", None)),
                format_func=lambda x: f"{x} {'Extremely Clear' if x == 5 else 'Extremely Unclear' if x == 1 else ''}" if x else "No Selection",
                key=f"clarity_{index}",
            )

            submit_button = st.form_submit_button("Submit Rating")

        if submit_button:
            if pleasantness is None or clarity is None:
                st.warning("Please provide a rating for both questions before submitting.")
            else:
                st.session_state.audio_ratings[row['poll_index']] = {
                    "pleasantness": pleasantness,
                    "clarity": clarity,
                    "Attack": row['Attack'],  # Save attack info in the background
                }

                # Save to database immediately
                supabase = get_supabase_client()
                uid = st.session_state.user_id
                data = {
                    "uid": uid,
                    "poll_index": int(row['poll_index']),  # Explicitly cast to int
                    "attack": row['Attack'],
                    "pleasantness": pleasantness,
                    "clarity": clarity,
                }
                response = supabase.table("audio_rating").upsert(data).execute()
                
                if response.data:  # Check if the response indicates success
                    st.session_state.current_audio_index += 1
                    st.session_state.show_indicator = True  # Show submission success message

                    if st.session_state.current_audio_index >= total_audios:
                        st.session_state.completed = True

                    st.rerun()
                else:
                    st.error("An error occurred while saving the data. Please try again.")

        # Show success indicator after submission
        if st.session_state.show_indicator:
            success_placeholder = st.empty()  # Create a placeholder for the success message
            success_placeholder.success("Rating submitted successfully!")
            time.sleep(0.9)  # Wait for 0.9 seconds
            success_placeholder.empty()  # Clear the message
            st.session_state.show_indicator = False

        # 'Go Back' Button
        if st.button("Go Back"):
            if st.session_state.current_audio_index > 0:
                st.session_state.current_audio_index -= 1
                st.rerun()
            else:
                st.warning("You are at the first audio sample.")

    # After completing the survey
    else:
        st.success("You have completed the audio rating survey.")

if __name__ == "__main__":
    main()
