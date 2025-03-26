import pandas as pd
import re
from jiwer import wer
from spellchecker import SpellChecker

def load_reference_transcriptions(csv_file):
    transcriptions = {}
    df = pd.read_csv(csv_file)
    for indx, row in df.iterrows():
        transcriptions[f'{indx}.wav'] = row['transcription']
    return transcriptions

def clean_text(text):
    """Clean text for WER calculation."""
    return re.sub(r'[^a-zA-Z\s]', '', text).lower()

def spellcheck_text(text):
    """
    Perform basic spellchecking on the provided text.
    
    Uses pyspellchecker to correct any misspelled words.
    """
    spell = SpellChecker()
    words = text.split()
    corrected_words = []
    for word in words:
        # If the word is misspelled, replace it with the correction
        if word.lower() not in spell:
            corrected = spell.correction(word)
            corrected_words.append(corrected if corrected is not None else word)
        else:
            corrected_words.append(word)
    return " ".join(corrected_words)
