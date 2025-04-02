
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
    """
    reference_transcriptions = load_reference_transcriptions(reference_file)
    supabase = get_supabase_client()
    data = {"uid": user_id}

    for parameter, audio_file in audio_assignments.items():
        transcription = transcriptions.get(parameter, None)
        if transcription is not None:
            transcription = spellcheck_text(transcription)
        audio_file_name = os.path.basename(audio_file)
        reference = reference_transcriptions.get(audio_file_name, "")

        if transcription and reference:
            error_rate = wer(clean_text(reference), clean_text(transcription))
            data[str(parameter)] = error_rate
        else:
            data[str(parameter)] = None

    try:
        response = supabase.table(table_name).upsert(data).execute()
        print(response)
        if response.data:
            print("Results saved successfully.")
        else:
            st.error(f"Failed to save results: {response}")
    except Exception as e:
        st.error(f"An error occurred while saving results: {e}")

    # Save raw transcription data as well
    try:
        save_raw_transcriptions(
            user_id=user_id,
            transcriptions=transcriptions,
            audio_assignments=audio_assignments,
            reference_file=reference_file,
            experiment_name=table_name
        )
    except Exception as e:
        st.error(f"Failed to save raw transcriptions: {e}")

def save_raw_transcriptions(user_id, transcriptions, audio_assignments, reference_file, experiment_name):
    reference_transcriptions = load_reference_transcriptions(reference_file)
    supabase = get_supabase_client()

    for parameter, audio_file in audio_assignments.items():
        user_transcription = transcriptions.get(parameter, None)
        if user_transcription is not None:
            user_transcription = spellcheck_text(user_transcription)

        audio_file_name = os.path.basename(audio_file)
        reference = reference_transcriptions.get(audio_file_name, "")

        row = {
            "uid": user_id,
            "parameter": str(parameter),
            "audio_file": audio_file_name,
            "user_transcription": user_transcription,
            "reference_transcription": reference,
            "experiment": experiment_name,
        }

        supabase.table("transcriptions_raw").upsert(row).execute()
