from utils.audio_processor import process_input
from core.transcriber import transcribe_all

source = "https://youtu.be/_Q-e_nczWqM?si=vrJ7zEEi77qy18TD"
audio_file = process_input(source)
transcription = transcribe_all([audio_file])