import os
from ollama import Client

client = Client(host=os.getenv("OLLAMA_HOST", "http://localhost:11434"))

def evaluate_transcription_quality(prompt: str) -> dict:
    """
    Evaluate a transcription-related prompt using a local LLM (via Ollama).
    Assumes the input 'prompt' includes both the system and user instructions.
    """
    print(f"Evaluating transcription: {prompt}")

    try:
        response = client.chat(
            model='mistral',
            messages=[{"role": "user", "content": prompt}]
        )
        feedback = response['message']['content'].strip()

        return {
            "evaluation": feedback
        }

    except Exception as e:
        return {
            "evaluation": f"Evaluation failed: {str(e)}"
        }
