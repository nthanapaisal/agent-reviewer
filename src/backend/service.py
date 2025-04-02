from backend.transcription.transcription import transcribe_file
from backend.prompts.prompts import build_prompt
from backend.evaluator.evaluator import evaluate_transcription_quality
from backend.analysis.analysis import generate_analysis

async def transcribe_audio(filepath: str) -> str:
    return transcribe_file(filepath)

def generate_prompts(transcription: str, user_prompt: str) -> str:
    return build_prompt(transcription, user_prompt)

def evaluate_transcription(prompt: str) -> dict:
    return evaluate_transcription_quality(prompt)

def create_analysis(evaluation: str) -> str:
    return generate_analysis(evaluation)
