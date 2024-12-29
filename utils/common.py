import os
import random
import streamlit as st

def assign_audio_files(base_dir, parameters):
    """
    Assigns one random audio file from a shared list for all parameters.
    Ensures no audio sample is selected more than once.

    Parameters:
        base_dir (str): Base directory containing subdirectories for each parameter.
        parameters (list): List of parameters corresponding to subdirectory names.

    Returns:
        dict: A dictionary where keys are parameters, and values are selected audio files.
    """
    audio_assignments = {}

    # Get the list of audio files from the first parameter's directory
    first_parameter_dir = os.path.normpath(os.path.join(base_dir, str(parameters[0])))
    if not os.path.exists(first_parameter_dir):
        st.error(f"Directory for parameter {parameters[0]} does not exist.")
        return audio_assignments

    # Generate the initial list of audio files
    shared_audio_files = [f for f in os.listdir(first_parameter_dir) if f.endswith(".wav")]
    if not shared_audio_files:
        st.error("No audio files found in the first parameter's directory.")
        return audio_assignments

    # Shuffle the audio files to ensure randomness
    random.shuffle(shared_audio_files)

    # Assign audio files to parameters
    for parameter in parameters:
        parameter_dir = os.path.normpath(os.path.join(base_dir, str(parameter)))

        if not os.path.exists(parameter_dir):
            st.error(f"Directory for parameter {parameter} does not exist.")
            continue

        if not shared_audio_files:
            st.error(f"No available audio files left for parameter {parameter}.")
            break

        # Pop an audio file from the shared list
        selected_audio = shared_audio_files.pop(0)

        # Construct the full path
        full_path = os.path.join(parameter_dir, selected_audio)
        full_path = full_path.replace("\\", "/")  # Normalize for forward slashes

        # Assign the selected file to the parameter
        audio_assignments[parameter] = full_path

    return audio_assignments