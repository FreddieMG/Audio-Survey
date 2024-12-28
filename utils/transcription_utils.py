import pandas as pd
import re
from jiwer import wer

def load_reference_transcriptions(csv_file):
    transcriptions = {}
    df = pd.read_csv(csv_file)
    for indx, row in df.iterrows():
        transcriptions[f'{indx}.wav'] = row['transcription']
    return transcriptions

def clean_text(text):
    """Clean text for WER calculation."""
    return re.sub(r'[^a-zA-Z\s]', '', text).lower()
