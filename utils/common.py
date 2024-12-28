import os
import random
import streamlit as st

def assign_audio_files(base_dir, parameters):
    print(base_dir)
    print(os.listdir(base_dir))
    """
    Assigns one random audio file from each subdirectory named after parameters.

    Parameters:
        base_dir (str): Base directory containing subdirectories for each parameter.
        parameters (list): List of parameters corresponding to subdirectory names.

    Returns:
        dict: A dictionary where keys are parameters, and values are selected audio files.
    """
    audio_assignments = {}

    for parameter in parameters:
        # Construct the subdirectory path for the parameter
        parameter_dir = os.path.join(base_dir, str(parameter))

        # Normalize the path to avoid backslash issues
        parameter_dir = os.path.normpath(parameter_dir)

        # Check if the directory exists
        if not os.path.exists(parameter_dir):
            print(parameter_dir)
            st.error(f"Directory for parameter {parameter} does not exist.")
            continue

        # Get the list of audio files in the subdirectory
        audio_files = [f for f in os.listdir(parameter_dir) if f.endswith(".wav")]

        if not audio_files:
            st.error(f"No audio files found in directory: {parameter_dir}")
            continue

        # Randomly select one audio file from the subdirectory
        selected_audio = random.choice(audio_files)

        # Normalize the full file path
        full_path = os.path.normpath(os.path.join(parameter_dir, selected_audio))
        full_path = full_path.replace("\\", "/")  # Convert backslashes to forward slashes
        audio_assignments[parameter] = full_path

    return audio_assignments