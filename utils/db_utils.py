from supabase import create_client
import streamlit as st
from utils.transcription_utils import load_reference_transcriptions, clean_text, spellcheck_text
from jiwer import wer
import os


# Initialize Supabase client
def get_supabase_client():
       
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

def save_results_to_supabase(user_id, table_name, transcriptions, audio_assignments, reference_file):
    """
    Saves transcription results with WER to the specified table in Supabase.

    Parameters:
        user_id (int): The user ID.
        table_name (str): The name of the Supabase table to save results.
        transcriptions (dict): The transcriptions to save, keyed by parameter.
        parameters (list): The column names corresponding to each parameter.
        reference_file (str): Path to the CSV file containing reference transcriptions.

    Returns:
        None
    """
    # Load reference transcriptions
    reference_transcriptions = load_reference_transcriptions(reference_file)

    # Get the Supabase client
    supabase = get_supabase_client()


    # Prepare the data payload
    data = {"uid": user_id}  # Start with the user ID
    for parameter, audio_file in audio_assignments.items():
        # Get the user transcription for the given parameter and run spellcheck
        transcription = transcriptions.get(parameter, None)
        if transcription is not None:
            transcription = spellcheck_text(transcription)
        audio_file_name = os.path.basename(audio_file)
        reference = reference_transcriptions.get(audio_file_name, "")

        # Calculate WER if both transcription and reference exist
        if transcription and reference:
            error_rate = wer(clean_text(reference), clean_text(transcription))
            data[str(parameter)] = error_rate
        else:
            data[str(parameter)] = None  # No data for this parameter

    # Insert or update the data in Supabase
    try:
        response = supabase.table(table_name).upsert(data).execute()

        # Print response for debugging
        print(response)

        # Check for success or errors
        if response.data:
            print("Results saved successfully.")
        else:
            st.error(f"Failed to save results: {response}")
    except Exception as e:
        st.error(f"An error occurred while saving results: {e}")